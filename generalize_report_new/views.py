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
from django.contrib.auth.models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import case, literal_column
# from paginateDemandReport import paginate_demand_report
from globalMethods import convert_to_millions,show_data_based_on_role,get_user_products
import aldjemy
import json
from datetime import datetime
from datetime import timedelta
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
            ins_general = GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('vchr_report_name','vchr_query','json_data','vchr_url_name','json_value')
            str_data = ins_general[0]['json_data']
            str_name = ins_general[0]['vchr_report_name']
            str_url_name = ins_general[0]['vchr_url_name']
            json_value = ins_general[0]['json_value'] if ins_general[0]['json_value'] else {}
            return Response({'status':'success','dct_details':str_data,'name':str_name,'url_name':str_url_name,'json_value':json_value})
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
            if ins_general:
                str_data = ins_general[0]['json_data']
            else:
                return JsonResponse({'status':'failed','data':'No Data'})

            fromdate =  datetime.strftime(datetime.strptime(request.data['date_from'], '%Y-%m-%d' ),'%Y-%m-%d')
            todate =  datetime.strftime(datetime.strptime(request.data['date_to'], '%Y-%m-%d' ),'%Y-%m-%d')
            branch_id = request.user.usermodel.fk_branch_id
            if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report']:
                str_filter = "dat_created_at::DATE between '"+str(fromdate)+"' AND '"+str(todate)+"'"
            elif ins_general[0]['vchr_url_name'] in ['mobilefinancereport']:
                str_filter = "em.dat_created_at::DATE between '"+str(fromdate)+"' AND '"+str(todate)+"'"
            elif ins_general[0]['vchr_url_name'] in ['stock_age_report']:
                str_filter = "bis.dat_stock::DATE <= '"+str(fromdate)+"'"


            else:
                str_filter = "dat_enquiry between '"+str(fromdate)+"' AND '"+str(todate)+"'"

            if request.user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','MARKETING','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report']:
                    str_filter += " AND branch.pk_bint_id = "+str(request.user.usermodel.fk_branch_id)
                elif ins_general[0]['vchr_url_name'] in ['mobilefinancereport','stock_age_report']:
                    str_filter += " AND br.pk_bint_id = "+str(request.user.usermodel.fk_branch_id)
                else:
                    str_filter += " AND branch_id = "+str(request.user.usermodel.fk_branch_id)
            elif request.user.usermodel.int_area_id:
                lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
                if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report']:
                    str_filter += " AND branch.pk_bint_id in ("+str(lst_branch)[1:-1]+")"
                elif ins_general[0]['vchr_url_name'] in ['mobilefinancereport']:
                    str_filter += " AND br.pk_bint_id in ("+str(lst_branch)[1:-1]+")"
                else:
                    str_filter += " AND branch_id in ("+str(lst_branch)[1:-1]+")"
            else:
                return Response({'status':'failed','reason':'No data'})


            if request.data.get('branchselected'):
                if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report']:
                    str_filter += " AND branch.pk_bint_id in ("+str(request.data.get('branchselected',[]))[1:-1]+")"
                elif ins_general[0]['vchr_url_name'] in ['mobilefinancereport']:
                    str_filter += " AND br.pk_bint_id in ("+str(request.data.get('branchselected',[]))[1:-1]+")"
                else:
                    str_filter += " AND branch_id in ("+str(request.data.get('branchselected',[]))[1:-1]+")"

            if len(request.data.get('custselected',[]))>0:
                str_filter+= " AND customer_mobile in ("+ str(request.data.get('custselected'))[1:-1]+")"

            if request.data.get('product'):
                str_filter += " AND product_id = "+str(request.data.get('product'))+""
                # rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_product_id == request.data.get('product'))
            if request.data.get('brand'):
                str_filter += " AND brand_id = "+str(request.data.get('brand'))+""
            # ======================================================================================================

            if request.data.get('productsselected'):
                if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report','mobilefinancereport']:
                    str_filter += " AND ie.fk_product_id in ("+str(request.data.get('productsselected',[]))[1:-1]+")"
                else:
                    str_filter += " AND product_id in ("+str(request.data.get('productsselected',[]))[1:-1]+")"
            if request.data.get('brandsselected'):
                if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report','mobilefinancereport']:
                    str_filter += " AND ie.fk_brand_id in ("+str(request.data.get('brandsselected',[]))[1:-1]+")"
                else:
                    str_filter += " AND brand_id in ("+str(request.data.get('brandsselected',[]))[1:-1]+")"

            if request.data.get('itemsselected'):
                if ins_general[0]['vchr_url_name'] in ['direct_discount_report','indirect_discount_report']:
                    str_filter += " AND ie.fk_item_id in ("+str(request.data.get('itemsselected',[]))[1:-1]+")"
                else:
                    str_filter += " AND item_id in ("+str(request.data.get('itemsselected',[]))[1:-1]+")"

            # ======================================================================================================

            if request.data.get('staffsselected'):
                str_filter += " AND user_id in ("+str(request.data.get('staffsselected',[]))[1:-1]+")"
            # todate = todate + timedelta(days = 1)
            # fromdate = request.data['date_from']
            # todate = request.data['date_to']
            if 'sales' in request.data['reportname']:
                str_report_type = 'SALE'
            else:
                str_report_type = 'ENQUIRY'
            ins_report = list(GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('vchr_report_name'))[0]['vchr_report_name']

            dct_data={}
            session=Session()
            # if ins_report.split(' ')[0].upper() == 'DEMAND' or ins_report.split(' ')[0].upper() == 'ZONE' or ins_report.split(' ')[0].upper() == 'TERRITORY' or ins_report.upper() == 'STATE REPORT' or ins_report.upper() == 'DAY WISE REPORT' or ins_report.upper() == 'PRODUCT PRICE RANGE REPORT':

            if request.data['show_type']:
                str_value = 'total_amount'
                if ins_general[0]['vchr_url_name'] in ['mobilefinancereport']:
                    str_value = 'ie.dbl_amount - ie.dbl_buy_back_amount - ie.dbl_discount_amount'
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

            str_chart1_chart2 = str_chart1+'_'+str_chart2
            str_chart1_chart3 = str_chart1+'_'+str_chart3
            str_chart1_chart4 = str_chart1+'_'+str_chart4
            str_chart1_chart5 = str_chart1+'_'+str_chart5
            str_chart1_chart6 = str_chart1+'_'+str_chart6
            str_chart1_chart7 = str_chart1+'_'+str_chart7
            str_chart1_chart8 = str_chart1+'_'+str_chart8
            str_chart1_chart9 = str_chart1+'_'+str_chart9
            str_chart1_chart10 = str_chart1+'_'+str_chart10

            str_chart1_chart2_chart3 = str_chart1+'_'+str_chart2+'_'+str_chart3
            str_chart1_chart2_chart4 = str_chart1+'_'+str_chart2+'_'+str_chart4
            str_chart1_chart2_chart5 = str_chart1+'_'+str_chart2+'_'+str_chart5
            str_chart1_chart2_chart6 = str_chart1+'_'+str_chart2+'_'+str_chart6
            str_chart1_chart2_chart7 = str_chart1+'_'+str_chart2+'_'+str_chart7
            str_chart1_chart2_chart8 = str_chart1+'_'+str_chart2+'_'+str_chart8
            str_chart1_chart2_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart9
            str_chart1_chart2_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart10

            str_chart1_chart2_chart3_chart4 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4
            str_chart1_chart2_chart3_chart5 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart5
            str_chart1_chart2_chart3_chart6 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart6
            str_chart1_chart2_chart3_chart7 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart7
            str_chart1_chart2_chart3_chart8 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart8
            str_chart1_chart2_chart3_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart9
            str_chart1_chart2_chart3_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart10

            str_chart1_chart2_chart3_chart4_chart5 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5
            str_chart1_chart2_chart3_chart4_chart6 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart6
            str_chart1_chart2_chart3_chart4_chart7 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart7
            str_chart1_chart2_chart3_chart4_chart8 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart8
            str_chart1_chart2_chart3_chart4_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart9
            str_chart1_chart2_chart3_chart4_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart10

            str_chart1_chart2_chart3_chart4_chart5_chart6 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6
            str_chart1_chart2_chart3_chart4_chart5_chart7 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart7
            str_chart1_chart2_chart3_chart4_chart5_chart8 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart8
            str_chart1_chart2_chart3_chart4_chart5_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart9
            str_chart1_chart2_chart3_chart4_chart5_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart10

            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7
            str_chart1_chart2_chart3_chart4_chart5_chart6_chart8 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart8
            str_chart1_chart2_chart3_chart4_chart5_chart6_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart9
            str_chart1_chart2_chart3_chart4_chart5_chart6_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart10

            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7+'_'+str_chart8
            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7+'_'+str_chart9
            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7+'_'+str_chart10

            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7+'_'+str_chart8+'_'+str_chart9
            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7+'_'+str_chart8+'_'+str_chart10

            str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10 = str_chart1+'_'+str_chart2+'_'+str_chart3+'_'+str_chart4+'_'+str_chart5+'_'+str_chart6+'_'+str_chart7+'_'+str_chart8+'_'+str_chart9+'_'+str_chart10

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
            'str_chart10': str_chart10,
            'str_chart1_chart2': str_chart1_chart2,
            'str_chart1_chart3': str_chart1_chart3,
            'str_chart1_chart4': str_chart1_chart4,
            'str_chart1_chart5': str_chart1_chart5,
            'str_chart1_chart6': str_chart1_chart6,
            'str_chart1_chart7': str_chart1_chart7,
            'str_chart1_chart8': str_chart1_chart8,
            'str_chart1_chart9': str_chart1_chart9,
            'str_chart1_chart10': str_chart1_chart10,
            'str_chart1_chart2_chart3': str_chart1_chart2_chart3,
            'str_chart1_chart2_chart4': str_chart1_chart2_chart4,
            'str_chart1_chart2_chart5': str_chart1_chart2_chart5,
            'str_chart1_chart2_chart6': str_chart1_chart2_chart6,
            'str_chart1_chart2_chart7': str_chart1_chart2_chart7,
            'str_chart1_chart2_chart8': str_chart1_chart2_chart8,
            'str_chart1_chart2_chart9': str_chart1_chart2_chart9,
            'str_chart1_chart2_chart10': str_chart1_chart2_chart10,
            'str_chart1_chart2_chart3_chart4': str_chart1_chart2_chart3_chart4,
            'str_chart1_chart2_chart3_chart5': str_chart1_chart2_chart3_chart5,
            'str_chart1_chart2_chart3_chart6': str_chart1_chart2_chart3_chart6,
            'str_chart1_chart2_chart3_chart7': str_chart1_chart2_chart3_chart7,
            'str_chart1_chart2_chart3_chart8': str_chart1_chart2_chart3_chart8,
            'str_chart1_chart2_chart3_chart9': str_chart1_chart2_chart3_chart9,
            'str_chart1_chart2_chart3_chart10': str_chart1_chart2_chart3_chart10,
            'str_chart1_chart2_chart3_chart4_chart5': str_chart1_chart2_chart3_chart4_chart5,
            'str_chart1_chart2_chart3_chart4_chart6': str_chart1_chart2_chart3_chart4_chart6,
            'str_chart1_chart2_chart3_chart4_chart7': str_chart1_chart2_chart3_chart4_chart7,
            'str_chart1_chart2_chart3_chart4_chart8': str_chart1_chart2_chart3_chart4_chart8,
            'str_chart1_chart2_chart3_chart4_chart9': str_chart1_chart2_chart3_chart4_chart9,
            'str_chart1_chart2_chart3_chart4_chart10': str_chart1_chart2_chart3_chart4_chart10,
            'str_chart1_chart2_chart3_chart4_chart5_chart6':str_chart1_chart2_chart3_chart4_chart5_chart6,
            'str_chart1_chart2_chart3_chart4_chart5_chart7':str_chart1_chart2_chart3_chart4_chart5_chart7,
            'str_chart1_chart2_chart3_chart4_chart5_chart8':str_chart1_chart2_chart3_chart4_chart5_chart8,
            'str_chart1_chart2_chart3_chart4_chart5_chart9':str_chart1_chart2_chart3_chart4_chart5_chart9,
            'str_chart1_chart2_chart3_chart4_chart5_chart10':str_chart1_chart2_chart3_chart4_chart5_chart10,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart8':str_chart1_chart2_chart3_chart4_chart5_chart6_chart8,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart9':str_chart1_chart2_chart3_chart4_chart5_chart6_chart9,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart10':str_chart1_chart2_chart3_chart4_chart5_chart6_chart10,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10,
            'str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10':str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10,
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

            dct_data[str_chart1_chart2] = {}
            dct_data[str_chart1_chart3] = {}
            dct_data[str_chart1_chart4] = {}
            dct_data[str_chart1_chart5] = {}
            dct_data[str_chart1_chart6] = {}
            dct_data[str_chart1_chart7] = {}
            dct_data[str_chart1_chart8] = {}
            dct_data[str_chart1_chart9] = {}
            dct_data[str_chart1_chart10] = {}

            dct_data[str_chart1_chart2_chart3] = {}
            dct_data[str_chart1_chart2_chart4] = {}
            dct_data[str_chart1_chart2_chart5] = {}
            dct_data[str_chart1_chart2_chart6] = {}
            dct_data[str_chart1_chart2_chart7] = {}
            dct_data[str_chart1_chart2_chart8] = {}
            dct_data[str_chart1_chart2_chart9] = {}
            dct_data[str_chart1_chart2_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4] = {}
            dct_data[str_chart1_chart2_chart3_chart5] = {}
            dct_data[str_chart1_chart2_chart3_chart6] = {}
            dct_data[str_chart1_chart2_chart3_chart7] = {}
            dct_data[str_chart1_chart2_chart3_chart8] = {}
            dct_data[str_chart1_chart2_chart3_chart9] = {}
            dct_data[str_chart1_chart2_chart3_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4_chart5] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart6] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart7] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart8] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart9] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9] = {}
            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10] = {}

            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10] = {}
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
                        dct_data[str_chart1][str_chart1_data]['Value1']= ins_data['value_2']
                    else:
                        dct_data[str_chart1][str_chart1_data]['Value1']= ins_data['value_1']
                        # Setting second value for the second bar
                        dct_data[str_chart1][str_chart1_data]['Value2'] = 0
                        if ((str_chart1_type == 'grouped_bar' or str_chart1_type == 'stacked_bar')):
                            dct_data[str_chart1][str_chart1_data]['Value2'] = ins_data['value_2']

                    dct_data[str_chart1_chart2][str_chart1_data]={}
                    dct_data[str_chart1_chart3][str_chart1_data]={}
                    dct_data[str_chart1_chart4][str_chart1_data]={}
                    dct_data[str_chart1_chart5][str_chart1_data]={}
                    dct_data[str_chart1_chart6][str_chart1_data]={}
                    dct_data[str_chart1_chart7][str_chart1_data]={}
                    dct_data[str_chart1_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart10][str_chart1_data]={}

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data] = {}
                    dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data] = {}
                    dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data] = {}
                    dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data] = {}
                    dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data] = {}
                    dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data] = {}
                    dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data] = {}
                    dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data] = {}

                    dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value2'] = 0
                    dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value2'] = 0
                    dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value2'] = 0
                    dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value2'] = 0
                    dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value2'] = 0
                    dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value2'] = 0
                    dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value2'] = 0
                    dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value2'] = 0
                    dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value2'] = 0


                    if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value2'] = ins_data['value_2']

                    if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                        dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value2'] = ins_data['value_2']

                    if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                        dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value2'] = ins_data['value_2']

                    if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                        dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value2'] = ins_data['value_2']

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value2'] = ins_data['value_2']

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value2'] = ins_data['value_2']

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value2'] = ins_data['value_2']

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value2'] = ins_data['value_2']

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value2'] = ins_data['value_2']


                    dct_data[str_chart1_chart2_chart3][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart4][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart5][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart6][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart7][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart10][str_chart1_data]={}


                    dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data]={}

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                    dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data] = {}
                    dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data] = {}
                    dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data] = {}
                    dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data] = {}
                    dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data] = {}
                    dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data] = {}

                    dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] = 0


                    if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] = ins_data['value_2']

                    if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar') ):
                        dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] = ins_data['value_2']

                    if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] = ins_data['value_2']

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] = ins_data['value_2']

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] = ins_data['value_2']

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] = ins_data['value_2']

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] = ins_data['value_2']

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] = ins_data['value_2']


                    dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data]={}


                    dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data]={}


                    dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data] = {}

                    dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value1'] =ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value1'] =ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value1'] =ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value1'] =ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value1'] =ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value1'] =ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value1'] =ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = 0

                    if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar') ):
                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = ins_data['value_2']

                    if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = ins_data['value_2']

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = ins_data['value_2']

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = ins_data['value_2']

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = ins_data['value_2']

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = ins_data['value_2']

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = ins_data['value_2']


                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data] = {}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value1'] = ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = 0

                    if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = ins_data['value_2']

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = ins_data['value_2']

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = ins_data['value_2']

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = ins_data['value_2']

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = ins_data['value_2']

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = ins_data['value_2']


                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data] = {}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1']= ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = 0

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = ins_data['value_2']

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = ins_data['value_2']

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = ins_data['value_2']

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = ins_data['value_2']

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = ins_data['value_2']


                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1']= ins_data['value_1']

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2']= 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2']= 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2']= 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2']= 0

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2']= ins_data['value_2']

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2']= ins_data['value_2']

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2']= ins_data['value_2']

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2']= ins_data['value_2']

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1']= ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1']= ins_data['value_1']

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = ins_data['value_2']
                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = ins_data['value_2']
                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1']=ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1']=ins_data['value_1']

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2']= 0
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2']= 0

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2']= ins_data['value_2']
                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2']= ins_data['value_2']

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]={}
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]={}

                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1']=ins_data['value_1']
                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2']=0

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2']=ins_data['value_2']

                else:
                    if ins_report.upper() == 'ZONE SALES REPORT' or ins_report.upper() == 'TERRITORY SALES REPORT':
                        dct_data[str_chart1][str_chart1_data]['Value1'] += ins_data['value_2']
                    else:
                        dct_data[str_chart1][str_chart1_data]['Value1'] += ins_data['value_1']

                        # Setting second value for the second bar

                        if ((str_chart1_type == 'grouped_bar' or str_chart1_type == 'stacked_bar')):
                            dct_data[str_chart1][str_chart1_data]['Value2'] += ins_data['value_2']

                    if str_chart2_data not in dct_data[str_chart1_chart2][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]= {}
                        dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value2'] = 0

                        if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value1'] += ins_data['value_1']

                        # Setting second value for the second bar

                        if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2][str_chart1_data][str_chart2_data]['Value2'] += ins_data['value_2']

                    if str_chart3_data not in dct_data[str_chart1_chart3][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]= {}
                        dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value2'] = 0

                        if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                            dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value1'] += ins_data['value_1']

                        # Setting second value for the second bar

                        if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                            dct_data[str_chart1_chart3][str_chart1_data][str_chart3_data]['Value2'] += ins_data['value_2']

                    if str_chart4_data not in dct_data[str_chart1_chart4][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]= {}
                        dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value2'] = 0

                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                            dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value1'] += ins_data['value_1']

                        # Setting second value for the second bar

                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                            dct_data[str_chart1_chart4][str_chart1_data][str_chart4_data]['Value2'] += ins_data['value_2']

                    if str_chart5_data not in dct_data[str_chart1_chart5][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]= {}
                        dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value2'] = 0

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value1']+= ins_data['value_1']

                        # Setting second value for the second bar

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart5][str_chart1_data][str_chart5_data]['Value2'] += ins_data['value_2']

                    if str_chart6_data not in dct_data[str_chart1_chart6][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value2'] = 0

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value1']+= ins_data['value_1']

                        # Setting second value for the second bar

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart6][str_chart1_data][str_chart6_data]['Value2'] += ins_data['value_2']


                    if str_chart7_data not in dct_data[str_chart1_chart7][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value1']+= ins_data['value_1']

                        # Setting second value for the second bar
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart7][str_chart1_data][str_chart7_data]['Value2'] += ins_data['value_2']

                    if str_chart8_data not in dct_data[str_chart1_chart8][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value1']+= ins_data['value_1']

                        # Setting second value for the second bar
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart8][str_chart1_data][str_chart8_data]['Value2'] += ins_data['value_2']

                    if str_chart9_data not in dct_data[str_chart1_chart9][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value1']+= ins_data['value_1']

                        # Setting second value for the second bar
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart9][str_chart1_data][str_chart9_data]['Value2'] += ins_data['value_2']

                    if str_chart10_data not in dct_data[str_chart1_chart10][str_chart1_data]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data] = {}
                        dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value2'] = ins_data['value_2']
                    else:
                        dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value1']+= ins_data['value_1']

                        # Setting second value for the second bar
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart10][str_chart1_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3][str_chart1_data]:
                        dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]= {}
                        dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]= {}
                        dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]= {}
                        dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]= {}
                        dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]= {}
                        dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]= {}
                        dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]= {}
                        dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]= {}

                        dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] = ins_data['value_2']
                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar') ):
                            dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] = ins_data['value_2']
                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] = ins_data['value_2']
                    else:
                        if str_chart3_data not in dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]={}
                            dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] = 0

                            if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3][str_chart1_data][str_chart2_data][str_chart3_data]['Value2'] += ins_data['value_2']

                        if str_chart4_data not in dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]= {}
                            dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value1']= ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] = 0

                            if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value1']+= ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart4][str_chart1_data][str_chart2_data][str_chart4_data]['Value2'] += ins_data['value_2']

                        if str_chart5_data not in dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]= {}
                            dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] = 0

                            if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart5][str_chart1_data][str_chart2_data][str_chart5_data]['Value2'] += ins_data['value_2']

                        if str_chart6_data not in dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]= {}
                            dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] = 0
                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart6][str_chart1_data][str_chart2_data][str_chart6_data]['Value2'] += ins_data['value_2']

                        if str_chart7_data not in dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]= {}
                            dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] = 0
                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart7][str_chart1_data][str_chart2_data][str_chart7_data]['Value2'] += ins_data['value_2']

                        if str_chart8_data not in dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]= {}
                            dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] = 0
                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart8][str_chart1_data][str_chart2_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        if str_chart9_data not in dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]= {}
                            dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] = 0
                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart9][str_chart1_data][str_chart2_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]= {}
                            dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] = 0
                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart10][str_chart1_data][str_chart2_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data]:

                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data]={}

                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]= {}

                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = 0


                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = ins_data['value_2']
                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar') ):
                            dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar') ):
                            dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar') ):
                            dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar') ):
                            dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar') ):
                            dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = ins_data['value_2']


                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data]:

                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]= {}

                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = 0


                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = ins_data['value_2']
                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    else:
                        if str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]={}

                            dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar

                            dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = 0
                            if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart5_data]['Value2'] += ins_data['value_2']


                        if str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = 0

                            if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]['Value2'] += ins_data['value_2']


                        if str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = 0

                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart6_data]['Value2'] += ins_data['value_2']

                        if str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = 0

                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart7_data]['Value2'] += ins_data['value_2']

                        if str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = 0

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        if str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = 0

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = 0

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    # edit
                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data]:
                        # 5 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        # 5 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value1']= ins_data['value_1']
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value1']= ins_data['value_1']
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value1']= ins_data['value_1']
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value1']= ins_data['value_1']
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value1']= ins_data['value_1']
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data]:
                        # 5 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]= {}
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]= {}
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]= {}
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]= {}
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]= {}
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]= {}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data]:
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]= {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = ins_data['value_2']
                    else:
                        if str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = 0

                            if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]['Value2'] += ins_data['value_2']
                        if str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = 0

                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart6_data]['Value2'] += ins_data['value_2']

                        if str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = 0

                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart7_data]['Value2'] += ins_data['value_2']

                        if str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = 0

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        if str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = 0

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]= {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value1'] = ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = 0

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value1'] += ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    # edit
                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data]:
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}


                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = ins_data['value_2']

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data]:
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1'] = ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1'] = ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = ins_data['value_2']

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data]:
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]={}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]= {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:
                        # 6 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 7 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 8 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 9 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}
                        # 10 th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]={}

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1']= ins_data['value_1']

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1']= ins_data['value_1']

                        # Setting second value for the second bar
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = 0
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    else:
                        if str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1']= ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = 0

                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value1']+= ins_data['value_1']

                            # Setting second value for the second bar

                            if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]['Value2'] += ins_data['value_2']

                        if str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data] = {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1']= ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = 0

                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value1']+= ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart7_data]['Value2'] += ins_data['value_2']

                        if str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data] = {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1']= ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = 0

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value1']+= ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        if str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data] = {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1']= ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = 0

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value1']+= ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:

                            # setting first value to be displayed on the graph in the dictionary
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data] = {}
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1']= ins_data['value_1']

                            # Setting second value for the second bar
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = 0

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value1']+= ins_data['value_1']

                            # Setting second value for the second bar
                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    # edit

                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data]:
                        #7th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        #8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}
                        #9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}
                        #10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data]:
                        #7th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        #8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}
                        #9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}
                        #10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data]:
                        #7th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        #8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}
                        #9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}
                        #10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:
                        #7th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        #8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}
                        #9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}
                        #10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:
                        # 7th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']
                    else:
                        if str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] = 0

                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']

                        else:

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value1'] += ins_data['value_1']
                            if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]['Value2'] += ins_data['value_2']

                        if str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] = 0

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        else:

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value1'] += ins_data['value_1']
                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        if str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] = 0

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        else:

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value1'] += ins_data['value_1']
                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] = 0

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']

                        else:

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value1'] += ins_data['value_1']
                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    # edit
                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data]:
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}

                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}

                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data]:
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}

                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}

                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data]:
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}

                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}

                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    elif str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                        # 8th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    else:
                        if str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] = 0

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value1'] += ins_data['value_1']

                            if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]['Value2'] += ins_data['value_2']

                        if str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] = 0

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value1'] += ins_data['value_1']

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] = 0

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value1'] += ins_data['value_1']

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart10_data]['Value2'] += ins_data['value_2']
                    # edit
                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}

                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]:
                        # 9th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']

                        # 10th chart
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']
                    else:
                        if str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = 0

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value1'] += ins_data['value_1']

                            if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]['Value2'] += ins_data['value_2']

                        if str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data] = {}

                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] = ins_data['value_1']
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = 0

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] = ins_data['value_2']
                        else:
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value1'] += ins_data['value_1']

                            if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart10_data]['Value2'] += ins_data['value_2']

                    # edit
                    if str_chart2_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data]:
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart3_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data]:

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart4_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data]:

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart5_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data]:

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart6_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data]:

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart7_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data]:
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart8_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data]:

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart9_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data]:
                         dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data] = {}
                         dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                         dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                         dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                         if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                             dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    elif str_chart10_data not in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data]:
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data] = {}

                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] = ins_data['value_1']
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] = ins_data['value_2']

                    else:
                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value1'] += ins_data['value_1']

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][str_chart1_data][str_chart2_data][str_chart3_data][str_chart4_data][str_chart5_data][str_chart6_data][str_chart7_data][str_chart8_data][str_chart9_data][str_chart10_data]['Value2'] += ins_data['value_2']

                if str_chart2_data not in dct_data[str_chart2]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart2][str_chart2_data] = {}
                    dct_data[str_chart2][str_chart2_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart2][str_chart2_data]['Value2'] = 0

                    if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                        dct_data[str_chart2][str_chart2_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart2][str_chart2_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar

                    if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                        dct_data[str_chart2][str_chart2_data]['Value2'] += ins_data['value_2']

                if str_chart3_data not in dct_data[str_chart3]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart3][str_chart3_data] = {}
                    dct_data[str_chart3][str_chart3_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart3][str_chart3_data]['Value2'] = 0

                    if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                        dct_data[str_chart3][str_chart3_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart3][str_chart3_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar

                    if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                        dct_data[str_chart3][str_chart3_data]['Value2'] += ins_data['value_2']

                if str_chart4_data not in dct_data[str_chart4]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart4][str_chart4_data] = {}
                    dct_data[str_chart4][str_chart4_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart4][str_chart4_data]['Value2'] = 0

                    if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                        dct_data[str_chart4][str_chart4_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart4][str_chart4_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar

                    if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                        dct_data[str_chart4][str_chart4_data]['Value2'] += ins_data['value_2']

                if str_chart5_data not in dct_data[str_chart5]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart5][str_chart5_data] = {}
                    dct_data[str_chart5][str_chart5_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart5][str_chart5_data]['Value2'] = 0

                    if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                        dct_data[str_chart5][str_chart5_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart5][str_chart5_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar

                    if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                        dct_data[str_chart5][str_chart5_data]['Value2'] += ins_data['value_2']
                if str_chart6_data not in dct_data[str_chart6]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart6][str_chart6_data] = {}
                    dct_data[str_chart6][str_chart6_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart6][str_chart6_data]['Value2'] = 0

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart6][str_chart6_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart6][str_chart6_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar

                    if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                        dct_data[str_chart6][str_chart6_data]['Value2'] += ins_data['value_2']

                if str_chart7_data not in dct_data[str_chart7]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart7][str_chart7_data] = {}
                    dct_data[str_chart7][str_chart7_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart7][str_chart7_data]['Value2'] = 0

                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart7][str_chart7_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart7][str_chart7_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar
                    if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                        dct_data[str_chart7][str_chart7_data]['Value2'] += ins_data['value_2']

                if str_chart8_data not in dct_data[str_chart8]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart8][str_chart8_data] = {}
                    dct_data[str_chart8][str_chart8_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart8][str_chart8_data]['Value2'] = 0

                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart8][str_chart8_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart8][str_chart8_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar
                    if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                        dct_data[str_chart8][str_chart8_data]['Value2'] += ins_data['value_2']

                if str_chart9_data not in dct_data[str_chart9]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart9][str_chart9_data] = {}
                    dct_data[str_chart9][str_chart9_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart9][str_chart9_data]['Value2'] = 0

                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart9][str_chart9_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart9][str_chart9_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar
                    if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                        dct_data[str_chart9][str_chart9_data]['Value2'] += ins_data['value_2']

                if str_chart10_data not in dct_data[str_chart10]:

                    # setting first value to be displayed on the graph in the dictionary
                    dct_data[str_chart10][str_chart10_data] = {}
                    dct_data[str_chart10][str_chart10_data]['Value1'] = ins_data['value_1']

                    # Setting second value for the second bar
                    dct_data[str_chart10][str_chart10_data]['Value2'] = 0

                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart10][str_chart10_data]['Value2'] = ins_data['value_2']
                else:
                    dct_data[str_chart10][str_chart10_data]['Value1'] += ins_data['value_1']

                    # Setting second value for the second bar
                    if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                        dct_data[str_chart10][str_chart10_data]['Value2'] += ins_data['value_2']
            # dct_data['table_data']=lst_table_data
            # paginating table data
            # ------------------------------------------------------------------
            # if request.data.get('show_table'):
            #     table_key = request.data.get('show_table')
            #     lst_table_data = []
            #     enq_total = 0
            #     if 'value_2' in rst_enquiry[0]:
            #         type = 'value_2'
            #     else:
            #         type = 'value_1'
            #     for data in dct_data[table_key]:
            #         enq_total += dct_data[table_key][data][type]
            #     for data in dct_data[table_key]:
            #         dct_table_data={}
            #         dct_table_data = dct_data[table_key][data]
            #         if table_key == 'staff_all':
            #             dct_table_data['Name'] = dct_data['staffs'][data]
            #         else:
            #             dct_table_data['Name'] = data
            #         dct_table_data['Contrib_per'] = round(dct_data[table_key][data][type]/enq_total*100,2)
            #         if type=='Sale':
            #             dct_table_data['Conversion_per'] = round(dct_data[table_key][data][type]/dct_data[table_key][data]['Enquiry']*100,2)
            #         lst_table_data.append(dct_table_data)
            #     return Response({'status':'success','table_data':lst_table_data})
            # ------------------------------------------------------------------

            if ins_report.split(' ')[0].upper() == 'DEMAND':
                dctFilter = list(GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('json_filter'))[0]['json_filter']
                dct_data = paginate_demand_report(request,dct_data,str_data)
                session.close()
                return Response({'status':'success','data':dct_data,'data_chart':dct_data_chart,'filter':dctFilter})
            # Chart1
            if str_data.get('1').get('type') == 'bar' or str_data.get('1').get('type') == 'grouped_bar' or str_data.get('1').get('type') == 'stacked_bar':
                if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                    dct_data[str_chart1]=topten_paginate_data(dct_data[str_chart1],10)
                else:
                    dct_data[str_chart1]=paginate_data(dct_data[str_chart1],10)

            # Chart2
            if str_data.get('2').get('type') == 'bar'or str_data.get('2').get('type') == 'grouped_bar' or str_data.get('2').get('type') == 'stacked_bar':
                if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                    dct_data[str_chart2]=topten_paginate_data(dct_data[str_chart2],10)
                else:
                    dct_data[str_chart2]=paginate_data(dct_data[str_chart2],10)
                for key in dct_data[str_chart1_chart2]:
                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                        dct_data[str_chart1_chart2][key]=topten_paginate_data(dct_data[str_chart1_chart2][key],10)
                    else:
                        dct_data[str_chart1_chart2][key]=paginate_data(dct_data[str_chart1_chart2][key],10)
            # Chart3
            if str_data.get('3'):
                if str_data.get('3').get('type') == 'bar' or str_data.get('3').get('type') == 'grouped_bar' or str_data.get('3').get('type') == 'stacked_bar':
                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                        dct_data[str_chart3]=topten_paginate_data(dct_data[str_chart3],10)
                    else:
                        dct_data[str_chart3]=paginate_data(dct_data[str_chart3],10)
                    for key in dct_data[str_chart1_chart3]:
                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                            dct_data[str_chart1_chart3][key]=topten_paginate_data(dct_data[str_chart1_chart3][key],10)
                        else:
                            dct_data[str_chart1_chart3][key]=paginate_data(dct_data[str_chart1_chart3][key],10)

                    for key in dct_data[str_chart1_chart2_chart3]:
                        for key1 in dct_data[str_chart1_chart2_chart3][key]:
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart1_chart2_chart3][key][key1]=topten_paginate_data(dct_data[str_chart1_chart2_chart3][key][key1],10)
                            else:
                                dct_data[str_chart1_chart2_chart3][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart3][key][key1],10)

            # Chart4
            if str_data.get('4'):
                if str_data.get('4').get('type') == 'bar' or str_data.get('4').get('type') == 'grouped_bar' or str_data.get('4').get('type') == 'stacked_bar':
                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                        dct_data[str_chart4]=topten_paginate_data(dct_data[str_chart4],10)
                    else:
                        dct_data[str_chart4]=paginate_data(dct_data[str_chart4],10)

                    for key in dct_data[str_chart1_chart4]:
                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                            dct_data[str_chart1_chart4][key]=topten_paginate_data(dct_data[str_chart1_chart4][key],10)
                        else:
                            dct_data[str_chart1_chart4][key]=paginate_data(dct_data[str_chart1_chart4][key],10)
                    for key in dct_data[str_chart1_chart2_chart4]:
                        for key1 in dct_data[str_chart1_chart2_chart4][key]:
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart1_chart2_chart4][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart4][key][key1],10)
                            else:
                                dct_data[str_chart1_chart2_chart4][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart4][key][key1],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4][key][key1]:
                                if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                    dct_data[str_chart1_chart2_chart3_chart4][key][key1][key2]=topten_paginate_data(dct_data[str_chart1_chart2_chart3_chart4][key][key1][key2],10)
                                else:
                                    dct_data[str_chart1_chart2_chart3_chart4][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4][key][key1][key2],10)

            #Chart5
            if str_data.get('5'):
                if str_data.get('5').get('type') == 'bar' or str_data.get('5').get('type') == 'grouped_bar' or str_data.get('5').get('type') == 'stacked_bar':
                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                        dct_data[str_chart5]=topten_paginate_data(dct_data[str_chart5],10)
                    else:
                        dct_data[str_chart5]=paginate_data(dct_data[str_chart5],10)
                    for key in dct_data[str_chart1_chart5]:
                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                            dct_data[str_chart1_chart5][key]=topten_paginate_data(dct_data[str_chart1_chart5][key],10)
                        else:
                            dct_data[str_chart1_chart5][key]=paginate_data(dct_data[str_chart1_chart5][key],10)

                    for key in dct_data[str_chart1_chart2_chart5]:
                        for key1 in dct_data[str_chart1_chart2_chart5][key]:
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart1_chart2_chart5][key][key1]=topten_paginate_data(dct_data[str_chart1_chart2_chart5][key][key1],10)
                            else:
                                dct_data[str_chart1_chart2_chart5][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart5][key][key1],10)

                    for key in dct_data[str_chart1_chart2_chart3_chart5]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart5][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart5][key][key1]:
                                if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                    dct_data[str_chart1_chart2_chart3_chart5][key][key1][key2]=topten_paginate_data(dct_data[str_chart1_chart2_chart3_chart5][key][key1][key2],10)
                                else:
                                    dct_data[str_chart1_chart2_chart3_chart5][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart5][key][key1][key2],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5][key][key1][key2]:
                                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                        dct_data[str_chart1_chart2_chart3_chart4_chart5][key][key1][key2][key3]=topten_paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5][key][key1][key2][key3],10)
                                    else:
                                        dct_data[str_chart1_chart2_chart3_chart4_chart5][key][key1][key2][key3]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5][key][key1][key2][key3],10)

            #Chart6
            if str_data.get('6'):
                if str_data.get('6').get('type') == 'bar' or str_data.get('6').get('type') == 'grouped_bar' or str_data.get('6').get('type') == 'stacked_bar':
                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                        dct_data[str_chart6]=topten_paginate_data(dct_data[str_chart6],10)
                    else:
                        dct_data[str_chart6]=paginate_data(dct_data[str_chart6],10)
                    for key in dct_data[str_chart1_chart6]:
                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                            dct_data[str_chart1_chart6][key]=topten_paginate_data(dct_data[str_chart1_chart6][key],10)
                        else:
                            dct_data[str_chart1_chart6][key]=paginate_data(dct_data[str_chart1_chart6][key],10)
                    for key in dct_data[str_chart1_chart2_chart6]:
                        for key1 in dct_data[str_chart1_chart2_chart6][key]:
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart1_chart2_chart6][key][key1]=topten_paginate_data(dct_data[str_chart1_chart2_chart6][key][key1],10)
                            else:
                                dct_data[str_chart1_chart2_chart6][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart6][key][key1],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart6]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart6][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart6][key][key1]:
                                if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                    dct_data[str_chart1_chart2_chart3_chart6][key][key1][key2]=topten_paginate_data(dct_data[str_chart1_chart2_chart3_chart6][key][key1][key2],10)
                                else:
                                    dct_data[str_chart1_chart2_chart3_chart6][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart6][key][key1][key2],10)

                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart6]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart6][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart6][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart6][key][key1][key2]:
                                    if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                        dct_data[str_chart1_chart2_chart3_chart4_chart6][key][key1][key2][key3]=topten_paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart6][key][key1][key2][key3],10)
                                    else:
                                        dct_data[str_chart1_chart2_chart3_chart4_chart6][key][key1][key2][key3]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart6][key][key1][key2][key3],10)

                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1][key2][key3]:
                                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1][key2][key3][key4]=topten_paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1][key2][key3][key4],10)
                                        else:
                                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1][key2][key3][key4]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6][key][key1][key2][key3][key4],10)

            #Chart7
            if str_data.get('7'):
                if str_data.get('7').get('type') == 'bar' or str_data.get('7').get('type') == 'grouped_bar' or str_data.get('7').get('type') == 'stacked_bar':
                    dct_data[str_chart7]=paginate_data(dct_data[str_chart7],10)
                    for key in dct_data[str_chart1_chart7]:
                            dct_data[str_chart1_chart7][key]=paginate_data(dct_data[str_chart1_chart7][key],10)
                    for key in dct_data[str_chart1_chart2_chart7]:
                        for key1 in dct_data[str_chart1_chart2_chart7][key]:
                            dct_data[str_chart1_chart2_chart7][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart7][key][key1],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart7]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart7][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart7][key][key1]:
                                dct_data[str_chart1_chart2_chart3_chart7][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart7][key][key1][key2],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart7]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart7][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart7][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart7][key][key1][key2]:
                                    dct_data[str_chart1_chart2_chart3_chart4_chart7][key][key1][key2][key3]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart7][key][key1][key2][key3],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][key][key1][key2][key3]:
                                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][key][key1][key2][key3][key4]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart7][key][key1][key2][key3][key4],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key][key1][key2][key3][key4]:
                                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key][key1][key2][key3][key4][key5]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7][key][key1][key2][key3][key4][key5],10)

            #Chart7
            if str_data.get('8'):
                if str_data.get('8').get('type') == 'bar' or str_data.get('8').get('type') == 'grouped_bar' or str_data.get('8').get('type') == 'stacked_bar':
                    dct_data[str_chart8]=paginate_data(dct_data[str_chart8],10)
                    for key in dct_data[str_chart1_chart8]:
                            dct_data[str_chart1_chart8][key]=paginate_data(dct_data[str_chart1_chart8][key],10)
                    for key in dct_data[str_chart1_chart2_chart8]:
                        for key1 in dct_data[str_chart1_chart2_chart8][key]:
                            dct_data[str_chart1_chart2_chart8][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart8][key][key1],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart8]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart8][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart8][key][key1]:
                                dct_data[str_chart1_chart2_chart3_chart8][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart8][key][key1][key2],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart8]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart8][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart8][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart8][key][key1][key2]:
                                    dct_data[str_chart1_chart2_chart3_chart4_chart8][key][key1][key2][key3]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart8][key][key1][key2][key3],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][key][key1][key2][key3]:
                                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][key][key1][key2][key3][key4]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart8][key][key1][key2][key3][key4],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key][key1][key2][key3][key4]:
                                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key][key1][key2][key3][key4][key5]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart8][key][key1][key2][key3][key4][key5],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1][key2][key3][key4]:
                                            for key6 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1][key2][key3][key4][key5]:
                                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1][key2][key3][key4][key5][key6]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8][key][key1][key2][key3][key4][key5][key6],10)

            #Chart9
            if str_data.get('9'):
                if str_data.get('9').get('type') == 'bar' or str_data.get('9').get('type') == 'grouped_bar' or str_data.get('9').get('type') == 'stacked_bar':
                    dct_data[str_chart9]=paginate_data(dct_data[str_chart9],10)
                    for key in dct_data[str_chart1_chart9]:
                            dct_data[str_chart1_chart9][key]=paginate_data(dct_data[str_chart1_chart9][key],10)
                    for key in dct_data[str_chart1_chart2_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart9][key]:
                            dct_data[str_chart1_chart2_chart9][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart9][key][key1],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart9][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart9][key][key1]:
                                dct_data[str_chart1_chart2_chart3_chart9][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart9][key][key1][key2],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart9][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart9][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart9][key][key1][key2]:
                                    dct_data[str_chart1_chart2_chart3_chart4_chart9][key][key1][key2][key3]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart9][key][key1][key2][key3],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][key][key1][key2][key3]:
                                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][key][key1][key2][key3][key4]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart9][key][key1][key2][key3][key4],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key][key1][key2][key3][key4]:
                                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key][key1][key2][key3][key4][key5]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart9][key][key1][key2][key3][key4][key5],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1][key2][key3][key4]:
                                            for key6 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1][key2][key3][key4][key5]:
                                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1][key2][key3][key4][key5][key6]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart9][key][key1][key2][key3][key4][key5][key6],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2][key3][key4]:
                                            for key6 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2][key3][key4][key5]:
                                                for key7 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2][key3][key4][key5][key6]:
                                                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2][key3][key4][key5][key6][key7]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9][key][key1][key2][key3][key4][key5][key6][key7],10)


            #Chart10
            if str_data.get('10'):
                if str_data.get('10').get('type') == 'bar' or str_data.get('10').get('type') == 'grouped_bar' or str_data.get('10').get('type') == 'stacked_bar':
                    dct_data[str_chart10]=paginate_data(dct_data[str_chart10],10)
                    for key in dct_data[str_chart1_chart10]:
                            dct_data[str_chart1_chart10][key]=paginate_data(dct_data[str_chart1_chart10][key],10)
                    for key in dct_data[str_chart1_chart2_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart10][key]:
                            dct_data[str_chart1_chart2_chart10][key][key1]=paginate_data(dct_data[str_chart1_chart2_chart10][key][key1],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart10][key][key1]:
                                dct_data[str_chart1_chart2_chart3_chart10][key][key1][key2]=paginate_data(dct_data[str_chart1_chart2_chart3_chart10][key][key1][key2],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart10][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart10][key][key1][key2]:
                                    dct_data[str_chart1_chart2_chart3_chart4_chart10][key][key1][key2][key3]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart10][key][key1][key2][key3],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][key][key1][key2][key3]:
                                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][key][key1][key2][key3][key4]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart10][key][key1][key2][key3][key4],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key][key1][key2][key3][key4]:
                                            dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key][key1][key2][key3][key4][key5]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart10][key][key1][key2][key3][key4][key5],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1][key2][key3][key4]:
                                            for key6 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1][key2][key3][key4][key5]:
                                                dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1][key2][key3][key4][key5][key6]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart10][key][key1][key2][key3][key4][key5][key6],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2][key3][key4]:
                                            for key6 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2][key3][key4][key5]:
                                                for key7 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2][key3][key4][key5][key6]:
                                                    dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2][key3][key4][key5][key6][key7]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart10][key][key1][key2][key3][key4][key5][key6][key7],10)
                    for key in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10]:
                        for key1 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key]:
                            for key2 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1]:
                                for key3 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2]:
                                    for key4 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3]:
                                        for key5 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3][key4]:
                                            for key6 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3][key4][key5]:
                                                for key7 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3][key4][key5][key6]:
                                                    for key8 in dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3][key4][key5][key6][key7]:
                                                        dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3][key4][key5][key6][key7][key8]=paginate_data(dct_data[str_chart1_chart2_chart3_chart4_chart5_chart6_chart7_chart8_chart9_chart10][key][key1][key2][key3][key4][key5][key6][key7][key8],10)

            # if ins_report.split(' ')[0].upper() == 'ZONE' or ins_report.split(' ')[0].upper() == 'TERRITORY' or ins_report.upper() == 'STATE REPORT' or ins_report.upper() == 'DAY WISE REPORT' or ins_report.upper() == 'PRODUCT PRICE RANGE REPORT':
            dctFilter = list(GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('json_filter'))[0]['json_filter']
            session.close()
            return Response({'status':'success','data':dct_data,'data_chart':dct_data_chart,'filter':dctFilter})
            # return Response({'status':'success','data':dct_data,'data_chart':dct_data_chart})
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
