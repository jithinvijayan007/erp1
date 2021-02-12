import re
import operator
from collections import Counter
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userdetails.models import UserDetails
from django.contrib.auth.models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import case, literal_column
import aldjemy
import json
from branch.models import Branch
from customer.models import CustomerDetails
from datetime import datetime,date
from datetime import timedelta
from titlecase import titlecase
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from export_excel.views import export_excel
from collections import OrderedDict


# import pandas as pd
from vincent.colors import brews
import random
from django.conf import settings
# from enquiry_mobile.tasks import email_sent

from vincent.colors import brews
# -------------------------------------
from django.shortcuts import render
import pandas as pd
from collections import OrderedDict
import operator
from django.core.mail import EmailMultiAlternatives
from os import path,makedirs,remove,listdir
from adminsettings.models import AdminSettings


def get_col_widths(dataframe):
    print("47")
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

def generate_excel(request,str_report,lst_details=None,dct_label=None,dct_data=None,lst_tbl_head=None,lst_tbl_index=None,dct_table_data=None):
    '''
    function used to export reports and table data in excel format
    parameter :request,report name,report data and table data
    reponse:return file name to download
    '''
    try:
        # import pdb; pdb.set_trace()

        lst_file=[]
        pie_chart_colour = []
        points =[{'fill': {'color': '#01c0c8'}},
                 {'fill': {'color': '#2ecc71'}},
                 {'fill': {'color': '#fb9678'}},
                 {'fill': {'color': '#799fb9'}},
                 {'fill': {'color': '#7e81cb'}},
                 {'fill': {'color': '#cf8595'}},
                 {'fill': {'color': '#9ea720'}},
                 {'fill': {'color': '#bd988b'}},
                 {'fill': {'color': '#008080'}},
                 {'fill': {'color': '#ff99cc'}},
                 {'fill': {'color': '#99ccff'}},
                 {'fill': {'color': '#00ffff'}},
                 {'fill': {'color': '#fba82c'}},
                 {'fill': {'color': '#b0b1a1'}},
                 {'fill': {'color': '#b156b1'}},
                 {'fill': {'color': '#cd3b42'}},
                 {'fill': {'color': '#4188cf'}},
                 {'fill': {'color': '#c18ff4'}},
                 {'fill': {'color': '#866668'}},
                 {'fill': {'color': '#757081'}},
                 {'fill': {'color': '#f4d03f'}}]

        # to handle staff name
        dct_staff = dct_data

        # Report colour from Adminsettings
        # if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='SALES_COLOUR',bln_enabled=True).vchr_value.exists():
        if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='SALES_COLOUR',bln_enabled=True).values_list('vchr_value',flat = True).first():
            sale_color = AdminSettings.objects.get(fk_company=request.user.userdetails.fk_company,vchr_code='SALES_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            sale_color = '#1f77b4'
        # if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).exists():
        if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).values_list('vchr_value',flat = True).first():
            enquiry_color = AdminSettings.objects.get(fk_company=request.user.userdetails.fk_company,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            enquiry_color='#aec7e8'

        colors=[enquiry_color,sale_color]
        # if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).exists():
        if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).values_list('vchr_value',flat = True).first():
            pie_chart_colour = AdminSettings.objects.get(fk_company=request.user.userdetails.fk_company,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).vchr_value
        # points = []
            points = [{'fill': {'color':i}} for i in pie_chart_colour]


        # table excel
        if request.data['bln_table']:
            # sheet for table
            if not request.data['bln_chart']:
                sheet_name1 = 'Sheet1'
                lst_tbl_head = lst_details
                lst_tbl_index = dct_label
                dct_table_data = dct_data
            else:
                sheet_name1 = 'Sheet2'
            all_data = {}
            # data for create table
            lst_all = list(zip(*dct_table_data))
            int_index = 0
            # create list for table creation
            while int_index< len(lst_tbl_head):
                all_data[str(int_index)+"_"+lst_tbl_head[int_index]] = lst_all[lst_tbl_index[int_index]]
                int_index +=1

            # create panda model of table data
            df = pd.DataFrame(all_data ,index = list(range(1,len(all_data["0_Enquiry No"])+1)))


            # Create a Pandas Excel writer using XlsxWriter as the engine.
            excel_file = settings.MEDIA_ROOT+'/Report.xlsx'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df.sort_values('0_Enquiry No').to_excel(writer,index=False, sheet_name=sheet_name1,startrow=6, startcol=0)
            # df.to_excel(writer, sheet_name=sheet_name1,startrow=6, startcol=0,index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name1]
            cell_format = workbook.add_format({'bold':True,'align': 'center'})
            int_ascii = 65

            for str_head in lst_tbl_head:
                worksheet.write(chr(int_ascii)+'7',str_head,cell_format)
                int_ascii +=1

            # format table style
            merge_format1 = workbook.add_format({
                'bold': 20,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':23
                })

            merge_format2 = workbook.add_format({
            'bold': 2,
            # 'border': 1,
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })

            # set column width
            for i,width in enumerate(get_col_widths(df)):
                worksheet.set_column(i-1, i-1, width)

            # create table heading and filter values
            worksheet.merge_range('A1+:M2', str_report, merge_format1)
            worksheet.merge_range('A3+:E3',"Report Period : "+datetime.strftime(datetime.strptime(request.data['date_from'], '%Y-%m-%d' ),'%d-%m-%Y')+" - "+datetime.strftime(datetime.strptime(request.data['date_to'] , '%Y-%m-%d' ),'%d-%m-%Y'))
            worksheet.merge_range('A4+:E4',"User :"+request.user.userdetails.first_name.title()+' '+request.user.userdetails.last_name.title())
            worksheet.merge_range('A5+:E5',"Report Date :"+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'))
            if request.data.get('branch'):
                branch_id = []
                branchId = request.data.get('branch',[])
                if type(branchId) == type(1):
                    branch_id.append(branchId)
                else:
                    branch_id = branchId
                rst_branch = list(Branch.objects.filter(pk_bint_id__in=branch_id).values('vchr_name'))
                # rst_branch = list(Branch.objects.filter(pk_bint_id__in=request.data.get('branch',[])).values('vchr_name'))
                str_branch = ''
                if rst_branch:
                    for ins_branch in rst_branch:
                        str_branch += ins_branch['vchr_name'].title()+'  ,'
                    str_branch = str_branch.rsplit(' ', 2)[0]
                    worksheet.merge_range('F3+:I3','Branch:'+str_branch)
            elif request.data.get('branchselected'):
                str_branch = list(Branch.objects.filter(pk_bint_id = request.data.get('branchselected')).values('vchr_name'))[0]['vchr_name']
                worksheet.merge_range('F3+:I3','Branch:'+str_branch.title())
            else:
                worksheet.merge_range('F3+:I3','Branch:Branch All')

            if request.data.get('staff'):
                lst_staff =[]
                staff_id = request.data.get('staff',[])
                if type(staff_id) == type(1):
                    lst_staff.append(staff_id)
                else:
                    lst_staff = staff_id
                rst_staff = list(User.objects.filter(id__in=lst_staff).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet.merge_range('F4+:I4','Staffs:'+str_staff)
            elif request.data.get('staffs'):
                staff_id = [i['id'] for i in request.data.get('staffs',[])]
                rst_staff = list(User.objects.filter(id__in=staff_id).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet.merge_range('F4+:I4','Staffs :'+str_staff)

            if request.data.get('custselected'):
                rst_customer = list(CustomerModel.objects.filter(cust_mobile__in=request.data.get('custselected',[])).values('cust_fname','cust_lname'))
                str_cust = ''
                for ins_cust in rst_customer:
                    str_cust +=ins_cust['cust_fname'].title()+' '+ins_cust['cust_lname'].title()+'  ,'
                str_cust = str_cust.rsplit(' ', 2)[0]
                worksheet.merge_range('F5+:I5','Customer :'+str_cust)


            # protect sheet from editing
            worksheet.protect()
# ========================================tabledata========================================================================================================================
        # create charts of reports
        if request.data['bln_chart'] :
            dct_all_data = {}
            dct_graph_data = {}
            str_type = ''

            if request.data.get('type'):
                str_type = request.data.get('type')
            # set data for chart creation
            for dct_name in lst_details:
                # data of bar chart
                if dct_name.split('-')[1].upper() == 'BAR':
                    dct_all_data[dct_name.split('-')[0]] =  dct_data[dct_name.split('-')[0]]
                else:#data of pie chart
                    dct_all_data[dct_name.split('-')[0]] =  dct_data[dct_name.split('-')[0]]
            for str_data in lst_details:
                dct_graph_data[str_data.split('-')[0]] = {}
                # Data for NA enquiry Report
                if str_report.upper() == 'NA ENQUIRY REPORT':
                    dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [x.title() for x in dct_all_data[str_data.split('-')[0]].keys()]
                    dct_graph_data[str_data.split('-')[0]]['Enquiry']=[int(i) for i in dct_all_data[str_data.split('-')[0]].values()]
                # Other Datas
                else:
                    if str_data.split('-')[1].upper() == 'BAR':
                        if str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                            str_key1 = 'NOT_COMPLETED'
                            str_key2 = 'COMPLETED'

                        elif str_report.upper() == " LMS PRODUCT REPORT":
                            str_key1 = 'Count'
                        elif str_report.upper() == 'FEEDBACK REPORT':
                            str_key1 = 'staff_rating'
                        else:

                            str_key1 = 'Enquiry'
                            str_key2 = 'Sale'
                        if str_data.split('-')[0] == 'staff_all' and str_report.upper() != " LMS STAFF REPORT" and str_report.upper() != "FEEDBACK REPORT":
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [dct_staff['staffs'][x].title() for i in dct_all_data[str_data.split('-')[0]] for x in i]
                        else:
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] =[list(x.keys())[0].title() for x in dct_all_data[str_data.split('-')[0]]]
                        dct_graph_data[str_data.split('-')[0]]['Enquiry']=[int(i[key][str_key1]) for i in dct_all_data[str_data.split('-')[0]] for key in i]
                        if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                            dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i[key][str_key2]) for i in dct_all_data[str_data.split('-')[0]] for key in i]
                        # elif str_report.upper() = " LMS STAFF REPORT" :
                        #     dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i[str_key1]) for i in dct_all_data[str_data.split('-')[0]].values()]
                    else:
                        if str_type.upper() =='SALE':
                            str_key = 'Sale'
                        elif str_type.upper() == 'ENQUIRY':
                            str_key = 'Enquiry'
                        else:
                            str_key = 'Count'

                        if str_data.split('-')[0] == 'staff_all' and str_report.upper() != " LMS STAFF REPORT":
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [dct_staff['staffs'][x].title() for x in dct_all_data[str_data.split('-')[0]].keys()]
                        elif str_report.upper() == 'FEEDBACK REPORT':
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [x for x in dct_all_data[str_data.split('-')[0]].keys()]
                        else:
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [x.title() for x in dct_all_data[str_data.split('-')[0]].keys()]

                        if str_type.upper() == 'SALE':
                            if str_data.split('-')[0] == 'staff_all' and str_report.upper() != " LMS STAFF REPORT":
                                dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i['Sale']) for i in dct_all_data[str_data.split('-')[0]].values()]
                            else:
                                dct_graph_data[str_data.split('-')[0]]['Sale']=[i for i in dct_all_data[str_data.split('-')[0]].values()]
                        else:
                            if type(list(dct_all_data[str_data.split('-')[0]].values())[0]) == type(1):
                                dct_graph_data[str_data.split('-')[0]]['Enquiry']=[i for i in dct_all_data[str_data.split('-')[0]].values()]
                            else:
                                dct_graph_data[str_data.split('-')[0]]['Enquiry']=[int(i[str_key]) for i in dct_all_data[str_data.split('-')[0]].values()]


            if str_type.upper() == 'ENQUIRY':
                lst_types = ['Enquiry']
            elif str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                lst_types = ['Enquiry',"Sale"]
            elif str_report.upper() == 'FEEDBACK REPORT':
                lst_types = ['Rating']
            else:
                # lst_types = ['Enquiry']
                lst_types = ['Enquiry',"Sale"]


            dct_df = {} #dictionary of DataFrame objects
            dct_chart = {} #dictionary of Chart objects
            if not request.data['bln_table']:
                excel_file = settings.MEDIA_ROOT+'/Report.xlsx'
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                workbook = writer.book

            for str_data in lst_details:
                if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                    dct_df[str_data.split('-')[0]]= pd.DataFrame(dct_graph_data[str_data.split('-')[0]], index = [i for i in range(1,len(dct_graph_data[str_data.split('-')[0]]["Sale"])+1)])
                else:
                    dct_df[str_data.split('-')[0]]= pd.DataFrame(dct_graph_data[str_data.split('-')[0]], index = [i for i in range(1,len(dct_graph_data[str_data.split('-')[0]]['Enquiry'])+1)])
                if str_data.split('-')[1].upper() == 'BAR':
                    dct_chart[str_data.split('-')[0]] = workbook.add_chart({'type': 'column'})
                else:
                    dct_chart[str_data.split('-')[0]] = workbook.add_chart({'type': 'pie'})

            # Create a Pandas Excel writer using XlsxWriter as the engine.


            sheet_name1 = 'Sheet1'

            row_num = 11
            for str_data in lst_details:
                dct_df[str_data.split('-')[0]].to_excel(writer,sheet_name=sheet_name1,startrow=row_num,startcol=9)
                row_num += 22


            # Access the XlsxWriter workbook and worksheet objects from the dataframe.

            worksheet1 = writer.sheets[sheet_name1]
            cell_format = workbook.add_format({'bold':False,'align': 'center'})


            merge_format = workbook.add_format({
            'bold': 0,
            # 'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size':17
            })
            merge_format2 = workbook.add_format({
            'bold': 0,
            'border': 1,
            'bg_color':'#ffffff',
            'font_color': '#000000',
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })
            merge_format3 = workbook.add_format({
            'bold': 0,
            'border': 1,
            'bg_color':'#d9d9d9',
            'font_color': '#000000',
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })
            merge_format4 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'font_color': '#000000',
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })
            merge_format1 = workbook.add_format({
            'bold': 15,
            # 'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size':21
            })



            # =================================chart1===================================
            head_row,head_column = 11,11
            name_row,value_row = 11,12
            int_graph_pos= 10
            for str_dct in lst_details:
                worksheet1.merge_range('J'+str(head_row)+'+:M'+str(head_column),dct_label[str_dct.split('-')[0]], merge_format)
            # chart chart_one

                if str_dct.split('-')[1].upper() == 'BAR':
                    if len(dct_graph_data[str_dct.split('-')[0]]['Enquiry']) <=5:
                        int_gap = 400000
                    elif len(dct_graph_data[str_dct.split('-')[0]]['Enquiry']) <=7:
                        if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                            int_gap = 300
                        else:
                            int_gap = 300
                    else:
                        if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                            int_gap = 170
                        else:
                            int_gap = 175
                    # print(int_gap)
                    for col_num in range(1, len(lst_types) + 1):
                        dct_chart[str_dct.split('-')[0]].add_series({
                        'name':       ['Sheet1', name_row ,10+col_num],
                        'categories': ['Sheet1', value_row, 9 ,len(dct_graph_data[str_dct.split('-')[0]]['Enquiry'])+name_row, 9],
                        'values':     ['Sheet1', value_row,10+col_num, len(dct_graph_data[str_dct.split('-')[0]]['Enquiry'])+name_row, 10+col_num],
                        'fill':       {'color':  colors[col_num - 1]},
                        'gap': int_gap,
                        'width':1,
                        })
                else:

                    if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                        dct_chart[str_dct.split('-')[0]].add_series({
                        'categories': ['Sheet1', value_row, 9,len(dct_graph_data[str_dct.split('-')[0]]['Sale'])+name_row, 9],
                        'values':     ['Sheet1', value_row, 11,len(dct_graph_data[str_dct.split('-')[0]]['Sale'])+name_row, 11],
                        'points': points,
                        'width':1,
                        })
                    else:
                        dct_chart[str_dct.split('-')[0]].add_series({
                        'categories': ['Sheet1', value_row, 9,len(dct_graph_data[str_dct.split('-')[0]]['Enquiry'])+name_row, 9],
                        'values':     ['Sheet1', value_row, 11,len(dct_graph_data[str_dct.split('-')[0]]['Enquiry'])+name_row, 11],
                        'points': points,
                        'width':1,
                        })
            # Add a chart title and some axis labels.
                dct_chart[str_dct.split('-')[0]].set_size({'width':550, 'height': 360})
                dct_chart[str_dct.split('-')[0]].set_title ({'name': dct_label[str_dct.split('-')[0]] })

            # Set an Excel chart style.
                dct_chart[str_dct.split('-')[0]].set_style(11)
            # Configure the chart axes.
                dct_chart[str_dct.split('-')[0]].set_y_axis({
                'major_gridlines': {'visible': False}
                })

                if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT" :
                    int_length = len(dct_graph_data[str_dct.split('-')[0]]['Sale'])
                    str_position = 'J'+str(value_row)+':M'+str(value_row)
                    str_position2 = 'K'+str(value_row+1)+'+:K'+str(value_row+int_length)
                    str_position3 = 'J'+str(value_row)+':M'+str(value_row+int_length)
                    str_position4 = 'J'+str(value_row+int_length+1)+':M'+str(value_row+int_length+1)
                else:
                    int_length = len(dct_graph_data[str_dct.split('-')[0]]['Enquiry'])
                    str_position = 'J'+str(value_row)+':L'+str(value_row)
                    str_position2 = 'K'+str(value_row)+':K'+str(value_row+int_length)
                    str_position3 = 'J'+str(value_row)+':L'+str(value_row+int_length)
                    str_position4 = 'J'+str(value_row+int_length+1)+':L'+str(value_row+int_length+1)


                worksheet1.conditional_format(str_position, {'type': 'cell',
                                                         'value': '@',
                                                         'criteria': 'containing',
                                                         'format':merge_format4
                                                         })
                worksheet1.conditional_format(str_position2, {'type': 'cell',
                                                         'value': '@@@@@',
                                                         'criteria': 'containing',
                                                         'format':merge_format2
                                                         })
                worksheet1.conditional_format(str_position3, {'type': 'cell',
                                                         'value': '1000000000',
                                                         'criteria': '<=',
                                                         'format':merge_format2
                                                         })
                worksheet1.conditional_format(str_position4, {'type': 'cell',
                                                         'value': 'text',
                                                         'criteria': 'containing',
                                                         'format':merge_format3
                                                         })
            # Insert the chart into the worksheet.
                worksheet1.insert_chart('A'+str(int_graph_pos), dct_chart[str_dct.split('-')[0]])
                head_row += 22
                head_column += 22
                name_row += 22
                value_row += 22
                int_graph_pos +=22

            today = date.today()
            worksheet1.merge_range('A10+:I'+str(int_graph_pos), '')
            worksheet1.set_column(10,10,35)
            # worksheet1.protect()
            worksheet1.merge_range('A1+:M2', str_report, merge_format)
            worksheet1.merge_range('A3+:E3',"Report Period : "+datetime.strftime(datetime.strptime(request.data['date_from'], '%Y-%m-%d' ),'%d-%m-%Y')+" - "+datetime.strftime(datetime.strptime(request.data['date_to'] , '%Y-%m-%d' ),'%d-%m-%Y'))
            worksheet1.merge_range('A4+:E4',"User :"+request.user.userdetails.first_name.title()+' '+request.user.userdetails.last_name.title())
            worksheet1.merge_range('A5+:E5',"Report Date :"+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'))
            if request.data.get('branch'):
                branch_id = []
                branchId = request.data.get('branch',[])
                if type(branchId) == type(1):
                    branch_id.append(branchId)
                else:
                    branch_id = branchId
                rst_branch = list(Branch.objects.filter(pk_bint_id__in=branch_id).values('vchr_name'))
                # rst_branch = list(Branch.objects.filter(pk_bint_id__in=request.data.get('branch',[])).values('vchr_name'))
                str_branch = ''
                if rst_branch:
                    for ins_branch in rst_branch:
                        str_branch += ins_branch['vchr_name'].title()+'  ,'
                    str_branch = str_branch.rsplit(' ', 2)[0]
                    worksheet1.merge_range('K3+:L3','Branch:'+str_branch)
            elif request.data.get('branchselected'):
                str_branch = list(Branch.objects.filter(pk_bint_id = request.data.get('branchselected')).values('vchr_name'))[0]['vchr_name']
                worksheet1.merge_range('K3+:L3','Branch :'+str_branch.title())
            else:
                worksheet1.merge_range('K3+:L3','Branch:Branch All')

            if request.data.get('staff'):
                lst_staff =[]
                staff_id = request.data.get('staff',[])
                if type(staff_id) == type(1):
                    lst_staff.append(staff_id)
                else:
                    lst_staff = staff_id
                rst_staff = list(User.objects.filter(id__in=lst_staff).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet1.merge_range('K4+:L4','Staffs :'+str_staff)

            elif request.data.get('staffs'):
                # staff_id = request.data.get('staffs')[0]['id']

                staff_id = [i['id'] for i in request.data.get('staffs',[])]
                rst_staff = list(User.objects.filter(id__in=staff_id).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet1.merge_range('K4+:L4','Staffs :'+str_staff)

            if request.data.get('custselected'):
                rst_customer = list(CustomerModel.objects.filter(cust_mobile__in=request.data.get('custselected','')).values('cust_fname','cust_lname'))
                str_cust = ''
                for ins_cust in rst_customer:
                    str_cust +=ins_cust['cust_fname'].title()+' '+ins_cust['cust_lname'].title()+'  ,'
                str_cust = str_cust.rsplit(' ', 2)[0]
                worksheet1.merge_range('K5+:L5','Customer :'+str_cust)

        writer.save()

        # if export_type.upper() == 'DOWNLOAD':
        if  request.data['export_type'].upper() == 'DOWNLOAD':
            data = settings.HOSTNAME+'/media/Report.xlsx'
            return data
        if request.data['export_type'].upper() == 'MAIL':
            filename = excel_file
            to = request.data.get('email').split(",")
            subject =  str_report
            from_email = settings.EMAIL_HOST_EMAIL
            text_content = 'Travidux'
            html_content = '''Dear, '''
            mail = EmailMultiAlternatives(subject, text_content, from_email, to)
            mail.attach_alternative(html_content, "text/html")
            mail.attach_file(filename)
            mail.send()
            remove(filename)
            # print("email-now")

            # email_sent(subject, text_content,from_email,to,html_content,filename)
            return data
            # return Response({'status':'success'})
    except Exception as msg:
            return msg



def general_generate_excel(request,str_report,lst_details=None,dct_label=None,dct_data=None,lst_tbl_head=None,lst_tbl_index=None,dct_table_data=None):
    '''
    function used to export reports and table data in excel format
    parameter :request,report name,report data and table data
    reponse:return file name to download
    '''
    # if request.data['reportname']=='branch_profit_report':
    #     str_

    try:

        str_data_name = 'Enquiry'
        if request.data['reportname'] in ['branch_profit_report','territory_profit_report','product_profit_report','zone_profit_report','item_profit_report','price_range_profit_report']:
            str_data_name = 'Profit'
        elif(request.data['reportname'] in ['reward_summary_report','reward_zone_report','reward_territory_report','reward_branch_report','reward_staff_report']):
            str_data_name = 'Reward'
        lst_file=[]
        pie_chart_colour = []
        points =[{'fill': {'color': '#01c0c8'}},
                 {'fill': {'color': '#2ecc71'}},
                 {'fill': {'color': '#fb9678'}},
                 {'fill': {'color': '#799fb9'}},
                 {'fill': {'color': '#7e81cb'}},
                 {'fill': {'color': '#cf8595'}},
                 {'fill': {'color': '#9ea720'}},
                 {'fill': {'color': '#bd988b'}},
                 {'fill': {'color': '#008080'}},
                 {'fill': {'color': '#ff99cc'}},
                 {'fill': {'color': '#99ccff'}},
                 {'fill': {'color': '#00ffff'}},
                 {'fill': {'color': '#fba82c'}},
                 {'fill': {'color': '#b0b1a1'}},
                 {'fill': {'color': '#b156b1'}},
                 {'fill': {'color': '#cd3b42'}},
                 {'fill': {'color': '#4188cf'}},
                 {'fill': {'color': '#c18ff4'}},
                 {'fill': {'color': '#866668'}},
                 {'fill': {'color': '#757081'}},
                 {'fill': {'color': '#f4d03f'}}]

        # to handle staff name
        dct_staff = dct_data

        # Report colour from Adminsettings
        if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='SALES_COLOUR',bln_enabled=True).exists():
            sale_color = AdminSettings.objects.get(fk_company=request.user.userdetails.fk_company,vchr_code='SALES_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            sale_color = '#1f77b4'
        if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).exists():
            enquiry_color = AdminSettings.objects.get(fk_company=request.user.userdetails.fk_company,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            enquiry_color='#aec7e8'

        colors=[enquiry_color,sale_color]
        if AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).exists():
            pie_chart_colour = AdminSettings.objects.get(fk_company=request.user.userdetails.fk_company,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).vchr_value
        # points = []
            points = [{'fill': {'color':i}} for i in pie_chart_colour]
        # import pdb;pdb.set_trace()
        # table excel
        if request.data['bln_table']:
            # sheet for table
            if not request.data['bln_chart']:
                sheet_name1 = 'Sheet1'
                lst_tbl_head = lst_details
                lst_tbl_index = dct_label
                dct_table_data = dct_data
            else:
                sheet_name1 = 'Sheet2'
            all_data = {}
            # data for create table
            lst_all = list(zip(*dct_table_data))
            int_index = 0
            # create list for table creation
            while int_index< len(lst_tbl_head):
                all_data[str(int_index)+"_"+lst_tbl_head[int_index]] = lst_all[lst_tbl_index[int_index]]
                int_index +=1

            # create panda model of table data
            df = pd.DataFrame(all_data ,index = list(range(1,len(all_data["0_Enquiry No"])+1)))

            # Create a Pandas Excel writer using XlsxWriter as the engine.
            excel_file = settings.MEDIA_ROOT+'/Report.xlsx'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df.sort_values('0_Enquiry No').to_excel(writer,index=False, sheet_name=sheet_name1,startrow=6, startcol=0)
            # df.to_excel(writer, sheet_name=sheet_name1,startrow=6, startcol=0,index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name1]
            cell_format = workbook.add_format({'bold':True,'align': 'center'})
            int_ascii = 65

            for str_head in lst_tbl_head:
                worksheet.write(chr(int_ascii)+'7',str_head,cell_format)
                int_ascii +=1

            # format table style
            merge_format1 = workbook.add_format({
                'bold': 20,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':50
                })

            merge_format2 = workbook.add_format({
            'bold': 2,
            # 'border': 1,
            'align': 'left',
            'valign': 'vleft',
            'font_size':30
            })

            # set column width
            for i,width in enumerate(get_col_widths(df)):
                worksheet.set_column(i-1, i-1, width)

            # create table heading and filter values
            worksheet.merge_range('A1+:M2', str_report, merge_format1)
            worksheet.merge_range('A3+:E3',"Report Period : "+datetime.strftime(datetime.strptime(request.data['date_from'], '%Y-%m-%d' ),'%d-%m-%Y')+" - "+datetime.strftime(datetime.strptime(request.data['date_to'] , '%Y-%m-%d' ),'%d-%m-%Y'))
            worksheet.merge_range('A4+:E4',"User :"+request.user.userdetails.first_name.title()+' '+request.user.userdetails.last_name.title())
            worksheet.merge_range('A5+:E5',"Report Date :"+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'))
            if request.data.get('branch'):
                branch_id = []
                branchId = request.data.get('branch',[])
                if type(branchId) == type(1):
                    branch_id.append(branchId)
                else:
                    branch_id = branchId
                rst_branch = list(Branch.objects.filter(pk_bint_id__in=branch_id).values('vchr_name'))
                # rst_branch = list(Branch.objects.filter(pk_bint_id__in=request.data.get('branch',[])).values('vchr_name'))
                str_branch = ''
                if rst_branch:
                    for ins_branch in rst_branch:
                        str_branch += ins_branch['vchr_name'].title()+'  ,'
                    str_branch = str_branch.rsplit(' ', 2)[0]
                    worksheet.merge_range('F3+:I3','Branch:'+str_branch)
            elif request.data.get('branchselected'):
                str_branch = list(Branch.objects.filter(pk_bint_id = request.data.get('branchselected')).values('vchr_name'))[0]['vchr_name']
                worksheet.merge_range('F3+:I3','Branch:'+str_branch.title())
            else:
                worksheet.merge_range('F3+:I3','Branch:Branch All')

            if request.data.get('staff'):
                lst_staff =[]
                staff_id = request.data.get('staff',[])
                if type(staff_id) == type(1):
                    lst_staff.append(staff_id)
                else:
                    lst_staff = staff_id
                rst_staff = list(User.objects.filter(id__in=lst_staff).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet.merge_range('F4+:I4','Staffs:'+str_staff)
            elif request.data.get('staffs'):
                staff_id = [i['id'] for i in request.data.get('staffs',[])]
                rst_staff = list(User.objects.filter(id__in=staff_id).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet.merge_range('F4+:I4','Staffs :'+str_staff)

            if request.data.get('custselected'):
                rst_customer = list(CustomerModel.objects.filter(cust_mobile__in=request.data.get('custselected',[])).values('cust_fname','cust_lname'))
                str_cust = ''
                for ins_cust in rst_customer:
                    str_cust +=ins_cust['cust_fname'].title()+' '+ins_cust['cust_lname'].title()+'  ,'
                str_cust = str_cust.rsplit(' ', 2)[0]
                worksheet.merge_range('F5+:I5','Customer :'+str_cust)


            # protect sheet from editing
            worksheet.protect()
# ========================================tabledata========================================================================================================================
        # create charts of reports
        if request.data['bln_chart'] :
            dct_all_data = {}
            dct_graph_data = {}

            # set data for chart creation
            for dct_name in lst_details:
                # data of bar chart
                if dct_name.split('-')[1].upper() == 'BAR' or dct_name.split('-')[1].upper() == 'GROUPED_BAR':
                    dct_all_data[dct_name.split('-')[0]] =  dct_data[dct_name.split('-')[0]]
                else:#data of pie chart
                    dct_all_data[dct_name.split('-')[0]] =  dct_data[dct_name.split('-')[0]]
            for str_data in lst_details:
                dct_graph_data[str_data.split('-')[0]] = {}
                # Data for NA enquiry Report
                if str_report.upper() == 'NA ENQUIRY REPORT':
                    dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [x.title() for x in dct_all_data[str_data.split('-')[0]].keys()]
                    dct_graph_data[str_data.split('-')[0]]['Enquiry']=[int(i) for i in dct_all_data[str_data.split('-')[0]].values()]
                # Other Datas
                else:
                    if str_data.split('-')[1].upper() == 'BAR' or str_data.split('-')[1].upper() == 'GROUPED_BAR':
                        if str_data.split('-')[0] == 'staff_all':
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [dct_staff['staffs'][x].title() for x in dct_all_data[str_data.split('-')[0]].keys()]
                        else:
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [list(x.keys())[0].title() for x in dct_all_data[str_data.split('-')[0]]]
                            # dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [x.title() for x in dct_all_data[str_data.split('-')[0]].keys()]
                        # dct_graph_data[str_data.split('-')[0]]['Enquiry']=[int(i['Value1']) for i in dct_all_data[str_data.split('-')[0]].values()]
                        dct_graph_data[str_data.split('-')[0]][str_data_name]=[int(i[key]['Value1']) for i in dct_all_data[str_data.split('-')[0]] for key in i]
                        if request.data['report_type'].upper() == 'SALE':
                            # dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i['Value2']) for i in dct_all_data[str_data.split('-')[0]].values()]
                            dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i[key]['Value2']) for i in dct_all_data[str_data.split('-')[0]] for key in i]
                    else:
                        if str_data.split('-')[0] == 'staff_all':
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [dct_staff['staffs'][x].title() for x in dct_all_data[str_data.split('-')[0]].keys()]
                        else:
                            dct_graph_data[str_data.split('-')[0]]["#"+dct_label[str_data.split('-')[0]].split(' ')[0]] = [x.title() for x in dct_all_data[str_data.split('-')[0]].keys()]

                        if request.data['report_type'].upper() == 'SALE':
                            if str_data.split('-')[0] == 'staff_all':
                                dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i['Value2']) for i in dct_all_data[str_data.split('-')[0]].values()]
                            else:
                                if str_report.upper() == 'TERRITORY SALES REPORT' or str_report.upper() == 'ZONE SALES REPORT':
                                    dct_graph_data[str_data.split('-')[0]]['Sale']=[int(i['Value1']) for i in dct_all_data[str_data.split('-')[0]].values()]
                                else:
                                    dct_graph_data[str_data.split('-')[0]]['Sale']=[i for i in dct_all_data[str_data.split('-')[0]].values()]
                        else:
                            if type(list(dct_all_data[str_data.split('-')[0]].values())[0]) == type(1):
                                dct_graph_data[str_data.split('-')[0]][str_data_name]=[i for i in dct_all_data[str_data.split('-')[0]].values()]
                            else:
                                dct_graph_data[str_data.split('-')[0]][str_data_name]=[int(i['Value1']) for i in dct_all_data[str_data.split('-')[0]].values()]

            if request.data['report_type'].upper() == 'ENQUIRY':
                lst_types = [str_data_name]
            else:
                lst_types = ['Enquiry','Sales']


            dct_df = {} #dictionary of DataFrame objects
            dct_chart = {} #dictionary of Chart objects
            if not request.data['bln_table']:
                excel_file = settings.MEDIA_ROOT+'/Report.xlsx'
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                workbook = writer.book

            for str_data in lst_details:
                if request.data['report_type'].upper() == 'ENQUIRY':
                    dct_df[str_data.split('-')[0]]= pd.DataFrame(dct_graph_data[str_data.split('-')[0]], index = [i for i in range(1,len(dct_graph_data[str_data.split('-')[0]][str_data_name])+1)])
                    # dct_df[str_data.split('-')[0]].
                else:
                    dct_df[str_data.split('-')[0]]= pd.DataFrame(dct_graph_data[str_data.split('-')[0]], index = [i for i in range(1,len(dct_graph_data[str_data.split('-')[0]]['Sale'])+1)])
                if str_data.split('-')[1].upper() == 'BAR' or str_data.split('-')[1].upper() == 'GROUPED_BAR':
                    dct_chart[str_data.split('-')[0]] = workbook.add_chart({'type': 'column'})
                else:
                    dct_chart[str_data.split('-')[0]] = workbook.add_chart({'type': 'pie'})

            # Create a Pandas Excel writer using XlsxWriter as the engine.


            sheet_name1 = 'Sheet1'

            row_num = 11
            for str_data in lst_details:
                dct_df[str_data.split('-')[0]].to_excel(writer,sheet_name=sheet_name1,startrow=row_num,startcol=9)
                row_num += 22


            # Access the XlsxWriter workbook and worksheet objects from the dataframe.

            worksheet1 = writer.sheets[sheet_name1]
            cell_format = workbook.add_format({'bold':False,'align': 'center'})


            merge_format = workbook.add_format({
            'bold': 4,
            # 'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size':14
            })
            merge_format2 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color':'#ffffff',
            'font_color': '#000000',
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })
            merge_format3 = workbook.add_format({
            'bold': 0,
            'border': 1,
            'bg_color':'#d9d9d9',
            'font_color': '#000000',
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })
            merge_format4 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'font_color': '#000000',
            'align': 'left',
            'valign': 'vleft',
            'font_size':10
            })
            merge_format1 = workbook.add_format({
            'bold': 15,
            # 'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size':21
            })



            # =================================chart1===================================
            head_row,head_column = 11,11
            name_row,value_row = 11,12
            int_graph_pos= 10
            for str_dct in lst_details:
                worksheet1.merge_range('J'+str(head_row)+'+:M'+str(head_column),dct_label[str_dct.split('-')[0]], merge_format)
            # chart chart_one
                # if str_dct.split('-')[1].upper() == 'BAR' or str_data.split('-')[1].upper() == 'GROUPED_BAR':
                if not str_dct.split('-')[1].upper() == 'PIE':
                    if len(dct_graph_data[str_dct.split('-')[0]][str_data_name]) ==1:
                        int_gap = 1000
                    elif len(dct_graph_data[str_dct.split('-')[0]][str_data_name]) ==2:
                        int_gap = 1000
                    elif len(dct_graph_data[str_dct.split('-')[0]][str_data_name]) <=5:
                        int_gap = 10000
                    elif len(dct_graph_data[str_dct.split('-')[0]][str_data_name]) <=7:
                        if request.data['report_type'].upper() == 'ENQUIRY':
                            int_gap = 300
                        else:
                            int_gap = 300
                    else:
                        if request.data['report_type'].upper() == 'ENQUIRY':
                            int_gap = 175
                        else:
                            int_gap = 170

                    for col_num in range(1, len(lst_types) + 1):
                        # import pdb; pdb.set_trace()

                        dct_chart[str_dct.split('-')[0]].add_series({
                        'name':       ['Sheet1', name_row ,10+col_num],
                        'categories': ['Sheet1', value_row, 9 ,len(dct_graph_data[str_dct.split('-')[0]][str_data_name])+name_row, 9],
                        'values':     ['Sheet1', value_row,10+col_num, len(dct_graph_data[str_dct.split('-')[0]][str_data_name])+name_row, 10+col_num],
                        'fill':       {'color':  colors[col_num - 1],'max':1},
                        'max':1,

                        # 'gap': 5
                        'gap': int_gap,
                        })


                else:

                    if request.data['report_type'].upper() == 'ENQUIRY':
                        dct_chart[str_dct.split('-')[0]].add_series({
                                'categories': ['Sheet1', value_row, 9,len(dct_graph_data[str_dct.split('-')[0]][str_data_name])+name_row, 9],
                                'values':     ['Sheet1', value_row, 11,len(dct_graph_data[str_dct.split('-')[0]][str_data_name])+name_row, 11],
                                'points': points,
                                'hoverinfo':'percentage',
                                'bar_width':1,
                                # 'data_labels': {'value': False,  # show value inside graph
                                #  'percentage': True,
                                 #  'separator': '\n',
                                #  'position': 'outside_end'},
                                # # 'size':10000000000,
                                })


                    else:
                        dct_chart[str_dct.split('-')[0]].add_series({
                                'categories': ['Sheet1', value_row, 9,len(dct_graph_data[str_dct.split('-')[0]]['Sale'])+name_row, 9],
                                'values':     ['Sheet1', value_row, 11,len(dct_graph_data[str_dct.split('-')[0]]['Sale'])+name_row, 11],
                                'points': points,
                                'width':1,
                                })
            # Add a chart title and some axis labels.
                dct_chart[str_dct.split('-')[0]].set_size({'width':550, 'height': 360})
                dct_chart[str_dct.split('-')[0]].set_title ({'name': dct_label[str_dct.split('-')[0]] })

            # Set an Excel chart style.
                dct_chart[str_dct.split('-')[0]].set_style(11)
            # Configure the chart axes.
                dct_chart[str_dct.split('-')[0]].set_y_axis({
                'major_gridlines': {'visible': False}
                })
            # Insert the chart into the worksheet.
                if request.data['report_type'].upper() == 'ENQUIRY':
                    int_length = len(dct_graph_data[str_dct.split('-')[0]][str_data_name])
                    str_position = 'J'+str(value_row)+':L'+str(value_row)
                    str_position2 = 'K'+str(value_row+1)+'+:K'+str(value_row+int_length)
                    str_position3 = 'J'+str(value_row)+':L'+str(value_row+int_length)
                    str_position4 = 'J'+str(value_row+int_length+1)+':L'+str(value_row+int_length+1)
                else:
                    int_length = len(dct_graph_data[str_dct.split('-')[0]]['Sale'])
                    str_position = 'J'+str(value_row)+':M'+str(value_row)
                    str_position2 = 'K'+str(value_row+1)+'+:K'+str(value_row+int_length)
                    str_position3 = 'J'+str(value_row)+':M'+str(value_row+int_length)
                    str_position4 = 'J'+str(value_row+int_length+1)+':M'+str(value_row+int_length+1)


                worksheet1.conditional_format(str_position, {'type': 'cell',
                                                         'value': '@',
                                                         'criteria': 'containing',
                                                         'format':merge_format4
                                                         })
                worksheet1.conditional_format(str_position2, {'type': 'cell',
                                                         'value': '@@@@@',
                                                         'criteria': 'containing',
                                                         'format':merge_format2
                                                         })
                worksheet1.conditional_format(str_position3, {'type': 'cell',
                                                         'value': '1000000000',
                                                         'criteria': '<=',
                                                         'format':merge_format2
                                                         })

                worksheet1.conditional_format(str_position4, {'type': 'cell',
                                                         'value': 'text',
                                                         'criteria': 'containing',
                                                         'format':merge_format3
                                                         })

                worksheet1.insert_chart('A'+str(int_graph_pos), dct_chart[str_dct.split('-')[0]])
                head_row += 22
                head_column += 22
                name_row += 22
                value_row += 22
                int_graph_pos +=22

            today = date.today()
            worksheet1.merge_range('A10+:I'+str(int_graph_pos), '')
            worksheet1.set_column(10,10,35)
            worksheet1.protect()
            worksheet1.merge_range('A1+:M2', str_report, merge_format)
            worksheet1.merge_range('A3+:E3',"Report Period : "+datetime.strftime(datetime.strptime(request.data['date_from'], '%Y-%m-%d' ),'%d-%m-%Y')+" - "+datetime.strftime(datetime.strptime(request.data['date_to'] , '%Y-%m-%d' ),'%d-%m-%Y'))
            worksheet1.merge_range('A4+:E4',"User :"+request.user.userdetails.first_name.title()+' '+request.user.userdetails.last_name.title())
            worksheet1.merge_range('A5+:E5',"Report Date :"+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'))
            if request.data.get('branchselected'):
                branch_id = []
                branchId = request.data.get('branchselected',[])
                if type(branchId) == type(1):
                    branch_id.append(branchId)
                else:
                    branch_id = branchId
                rst_branch = list(Branch.objects.filter(pk_bint_id__in=branch_id).values('vchr_name'))
                # rst_branch = list(Branch.objects.filter(pk_bint_id__in=request.data.get('branch',[])).values('vchr_name'))
                str_branch = ''
                if rst_branch:
                    for ins_branch in rst_branch:
                        str_branch += ins_branch['vchr_name'].title()+'  ,'
                    str_branch = str_branch.rsplit(' ', 2)[0]
                    worksheet1.merge_range('K3+:L3','Branch:'+str_branch)
            else:
                worksheet1.merge_range('K3+:L3','Branch:Branch All')

            if request.data.get('staff'):
                lst_staff =[]
                staff_id = request.data.get('staff',[])
                if type(staff_id) == type(1):
                    lst_staff.append(staff_id)
                else:
                    lst_staff = staff_id
                rst_staff = list(User.objects.filter(id__in=lst_staff).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet1.merge_range('K4+:L4','Staffs :'+str_staff)

            elif request.data.get('staffs'):
                # staff_id = request.data.get('staffs')[0]['id']

                staff_id = [i['id'] for i in request.data.get('staffs',[])]
                rst_staff = list(User.objects.filter(id__in=staff_id).values('first_name','last_name'))
                str_staff = ''
                if rst_staff:
                    for ins_staff in rst_staff:
                        str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                    str_staff = str_staff.rsplit(' ', 2)[0]
                    worksheet1.merge_range('K4+:L4','Staffs :'+str_staff)

            if request.data.get('custselected'):
                rst_customer = list(CustomerModel.objects.filter(cust_mobile__in=request.data.get('custselected','')).values('cust_fname','cust_lname'))
                str_cust = ''
                for ins_cust in rst_customer:
                    str_cust +=ins_cust['cust_fname'].title()+' '+ins_cust['cust_lname'].title()+'  ,'
                str_cust = str_cust.rsplit(' ', 2)[0]
                worksheet1.merge_range('K5+:L5','Customer :'+str_cust)

        writer.save()

        # if export_type.upper() == 'DOWNLOAD':
        if  request.data['export_type'].upper() == 'DOWNLOAD':
            data = settings.HOSTNAME+'/media/Report.xlsx'
            return data
        if request.data['export_type'].upper() == 'MAIL':
            filename = excel_file
            to = request.data.get('email').split(",")
            subject =  str_report
            from_email = settings.EMAIL_HOST_EMAIL
            text_content = 'Travidux'
            html_content = '''Dear, '''
            mail = EmailMultiAlternatives(subject, text_content, from_email, to)
            mail.attach_alternative(html_content, "text/html")
            mail.attach_file(filename)
            mail.send()
            remove(filename)
            # print("email-now")

            # email_sent(subject, text_content,from_email,to,html_content,filename)
            return Response({'status': 1})
    except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})
