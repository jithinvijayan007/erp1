from POS import ins_logger
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from datetime import timedelta
import pdfkit
import base64
from django.core.mail import EmailMultiAlternatives
from os import remove
from adminsettings.models import AdminSettings
from branch.models import Branch
from customer.models import CustomerDetails
from django.contrib.auth.models import User



def generate_pdf(request,str_report,lst_details=None,dct_label=None,dct_data=None,lst_tbl_head=None,lst_tbl_index=None,dct_table_data=None):
    space_count = 1
    """
    used to generate pdf of reports
    parameter : request,report name,chart details,table details
    return: file name.
    """
    try:
        lst_file=[]
        pie_chart_colour = []
        # import pdb; pdb.set_trace()
        # chart colour from admin settings
        # if AdminSettings.objects.filter(fk_company=1,vchr_code='SALES_COLOUR',bln_enabled=True).exists():
        if AdminSettings.objects.filter(fk_company=1,vchr_code='SALES_COLOUR',bln_enabled=True).values_list('vchr_value',flat = True).first():
            sale_color = AdminSettings.objects.get(fk_company=1,vchr_code='SALES_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            sale_color = '#1f77b4'
        # if AdminSettings.objects.filter(fk_company=1,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).exists():
        if AdminSettings.objects.filter(fk_company=1,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).values_list('vchr_value',flat = True).first():
            enquiry_color = AdminSettings.objects.get(fk_company=1,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            enquiry_color='#aec7e8'

        lst_color=[enquiry_color,sale_color]
        # if AdminSettings.objects.filter(fk_company=1,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).exists():
        if AdminSettings.objects.filter(fk_company=1,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).values_list('vchr_value',flat = True).first():
            pie_chart_colour = AdminSettings.objects.get(fk_company=1,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).vchr_value

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
        elif request.data.get('branchselected'):
            str_branch = list(Branch.objects.filter(pk_bint_id = request.data.get('branchselected')).values('vchr_name'))[0]['vchr_name']


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
        elif request.data.get('staffs'):
            staff_id = [i['id'] for i in request.data.get('staffs',[])]
            rst_staff = list(User.objects.filter(id__in=staff_id).values('first_name','last_name'))
            str_staff = ''
            if rst_staff:
                for ins_staff in rst_staff:
                    str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                str_staff = str_staff.rsplit(' ', 2)[0]

        if request.data.get('custselected'):
            rst_customer = list(CustomerModel.objects.filter(cust_mobile__in=request.data.get('custselected',[])).values('cust_fname','cust_lname'))
            str_cust = ''
            for ins_cust in rst_customer:
                str_cust +=ins_cust['cust_fname'].title()+' '+ins_cust['cust_lname'].title()+'  ,'
            str_cust = str_cust.rsplit(' ', 2)[0]

        pdf_path = settings.MEDIA_ROOT+'/'
        lst_status_all = []
        lst_status_all_show = []
        #
        # chart generation
        if request.data['bln_chart']:

            dct_details={}
            dct_pie_details = {}
            lst_pie_data = []
            str_type = ''
            if request.data.get('type'):
                str_type = request.data.get('type')
            for details in lst_details:
                if details.split('-')[1].upper() =='BAR': # DATA TO BAR CHART
                    if str_report == 'NA Enquiry Report': # NA ENQUIRY BAR CHART
                        lst_item = ['x']
                        lst_name = [details.split('-')[0]]
                        tbl_data =''
                        i=1
                        for item in dct_data[details.split('-')[0]]:
                            name=''
                            if details=='staff_all':# IN STAFF,STAFF CODE CHANGE TO STAFF NAME
                                name=dct_data['staffs'][item]
                            else:
                                name=item
                            if len(name)>31:
                                name=name[:29]+"..."
                            lst_item.append(i)
                            lst_name.append(int(dct_data[details.split('-')[0]][1][item]))
                            # TABLE DATA TO DISPLAY RIGHT SIDE OF CHART
                            tbl_data+='<tr><td>'+str(i)+'</td><td>'+str(name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][1][item])+'</td></tr>'
                            i+=1
                            dct_details[details.split('-')[0]]=[dct_label[details.split('-')[0]],lst_item,lst_name,tbl_data]
                    elif str_report == 'Feedback Report':
                        lst_item = ['x']
                        lst_name = [details.split('-')[0]]
                        tbl_data =''
                        i=0

                        for item in dct_data[details.split('-')[0]]:
                            name=''
                            if details=='staff_all':# IN STAFF,STAFF CODE CHANGE TO STAFF NAME
                                name=dct_data['staffs'][item]
                            else:
                                name=list(item.keys())[0]
                            if len(name)>31:
                                name=name[:29]+"..."
                            lst_item.append(i+1)
                            lst_name.extend(list(dct_data[details.split('-')[0]][i][name].values()))
                            # TABLE DATA TO DISPLAY RIGHT SIDE OF CHART
                            tbl_data+='<tr><td>'+str(i)+'</td><td>'+str(name)+'</td><td align="right">'+str(list(dct_data[details.split('-')[0]][i][name].values())[0])+'</td></tr>'
                            i+=1
                            dct_details[details.split('-')[0]]=[dct_label[details.split('-')[0]],lst_item,lst_name,tbl_data]
                    else:#BAR CHART OF ALL OTHER REPORTS
                        lst_item = ['x']
                        # LMS REPORTS

                        if str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                            lst_enquiry = ['NOT_COMPLETED']
                            lst_sale = ['COMPLETED']
                            str_key1 = 'NOT_COMPLETED'
                            str_key2 = 'COMPLETED'

                            # LMS PRODUCT REPORTS
                        elif str_report.upper() == " LMS PRODUCT REPORT":
                            str_key1 = 'Count'
                            lst_enquiry = ['COUNT']
                            lst_sale = []
                        else:# ALL OTHER REPORTS
                            lst_enquiry = ['Enquiry']
                            lst_sale = ['Sale']
                            str_key1 = 'Enquiry'
                            str_key2 = 'Sale'
                        tbl_data =''
                        i=0

                        for item in dct_data[details.split('-')[0]]:
                            name=''
                            if details.split('-')[0] =='staff_all' and str_report.upper() != " LMS STAFF REPORT":
                                str_name=dct_data['staffs'][int(*(item.keys()))]
                                name=int(*(item.keys()))
                            else:
                                str_name=name=list(item.keys())[0]
                            if len(str_name)>31:
                                str_name=str_name[:29]+"..."
                            lst_item.append(i+1) #list for index
                            lst_enquiry.append(int(dct_data[details.split('-')[0]][i][name][str_key1])) #list for enquiry/lms not_completed data
                            if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == ' LMS STAFF REPORT' or  str_report.upper() == " LMS BRANCH REPORT":
                                lst_sale.append(int(dct_data[details.split('-')[0]][i][name][str_key2])) #list for sale/lms completed data
                                # data for table creation corresponding chart
                                tbl_data+='<tr><td>'+str(i+1)+'</td><td>'+str(str_name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][i][name][str_key1])+'</td><td align="right">'+str(dct_data[details.split('-')[0]][i][name][str_key2])+'</td></tr>'
                            elif  str_report.upper() == " LMS PRODUCT REPORT ":# chart table lms product report
                                tbl_data+='<tr><td>'+str(i+1)+'</td><td>'+str(str_namestr_name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][1][item][str_key1])+'</td></tr>'
                            else:# chart table enquiry report
                                tbl_data+='<tr><td>'+str(i+1)+'</td><td>'+str(str_name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][i][name][str_key1])+'</td></tr>'
                            i+=1
                            dct_details[details.split('-')[0]]=[dct_label[details.split('-')[0]],lst_item,lst_enquiry,lst_sale,tbl_data]
                elif details.split('-')[1].upper() =='PIE': #DATA TO GENERATE PIE CHART
                    int_no = 1
                    str_status = ''
                    if str_type.upper() == 'SALE':
                        str_key = 'Sale'
                    elif str_type.upper() =='ENQUIRY':
                        str_key = 'Enquiry'
                    else:
                        str_key = 'Count'
                    dct_pie_details[details.split('-')[0]] = []
                    for str_data in dct_data[details.split('-')[0]]:
                        if not type(dct_data[details.split('-')[0]][str_data]) == type(1):
                            if details.split('-')[0] =='staff_all':
                                name=dct_data['staffs'][str_data]
                            else:
                                name=str_data

                            lst_status_all.append(dct_label[details.split('-')[0]])
                            lst_pie_data.append(name)
                            lst_pie_data.append(str(dct_data[details.split('-')[0]][str_data][str_key]))
                            dct_pie_details[details.split('-')[0]].append(list(lst_pie_data))
                            str_status += '''<tr><td>'''+str(int_no)+'''</td><td>'''+str(name)+'''</td><td>'''+str(dct_data[details.split('-')[0]][str_data][str_key])+'''</td></tr>'''
                            lst_status_all.append(str_status)
                            lst_status_all_show = lst_status_all
                            dct_details[details.split('-')[0]] = lst_status_all_show
                            lst_pie_data = []
                            lst_status_all = []
                            lst_status_all_show = []
                            int_no +=1
                        else:
                            if details.split('-')[0] =='staff_all':
                                name=dct_data['staffs'][str_data]
                            else:
                                name=str_data
                            lst_status_all.append(dct_label[details.split('-')[0]])
                            lst_pie_data.append(name)
                            lst_pie_data.append(str(dct_data[details.split('-')[0]][str_data]))
                            dct_pie_details[details.split('-')[0]].append(list(lst_pie_data))

                            str_status += '''<tr><td>'''+str(int_no)+'''</td><td>'''+str(name)+'''</td><td>'''+str(dct_data[details.split('-')[0]][str_data])+'''</td></tr>'''
                            lst_status_all.append(str_status)
                            lst_status_all_show = lst_status_all
                            dct_details[details.split('-')[0]] = lst_status_all_show
                            lst_pie_data = []
                            lst_status_all = []
                            lst_status_all_show = []
                            int_no +=1
            #HTML FOR TABLE CORRESPONDING CHART
            html_data = """<!DOCTYPE HTML>
                            <html>
                            <head>
                                <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>
                                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                            </head>
                            <body style="font-family: sans-serif; font-size: 14px;">
                              <div style="width:1000px; height:100%; margin:0 auto; padding:0px 30px; float:center; border:1px solid #000;">
                                  <br>
                                  <h3 class="text-center"><b style="color:#31708f !important;">"""+str_report+"""</b></h3>
                                  <br>
                                    <div class="row" style="padding:15px;">
                                      <div class="col-sm-7 col-xs-7">
                                        <div class="row"><div class="col-sm-3 col-xs-3"><b>From</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                        <div class="row"><div class="col-sm-3 col-xs-3"><b>To</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                        <div class="row"><div class="col-sm-3 col-xs-3"><b>Taken By</b></div><div class="col-sm-9 col-xs-9">"""+request.user.first_name+" "+request.user.last_name+"""</div></div>
                                      </div>
                                      <div class="col-sm-5 col-xs-5">"""
            if request.data.get('branch') or request.data.get('branchselected'):
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b> </div><div class="col-sm-7 col-xs-7">"""+str_branch+"""</div></div>"""
            else:
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b></div><div class="col-sm-7 col-xs-7">All</div></div>"""
            if request.data.get('staff') or request.data.get('staffs'):
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">"""+str_staff+"""</div></div>"""
            # else:
            #     html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">All</div></div>"""
            if request.data.get('custselected'):
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Customer</b> </div><div class="col-sm-7 col-xs-7">"""+str_cust+"""</div></div>"""
            html_data+="""<div class="row"><div class="col-sm-5 col-xs-5"><b>Action Date</b></div><div class="col-sm-7 col-xs-7"><span>"""+datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p")+"""</span></div></div></div></div><br>"""
            int_cont = 0

            for details in lst_details:
                if details.split('-')[1].upper() =='BAR':
                    if not str_report == 'NA Enquiry Report' and str_report != 'Feedback Report':
                        space_count=space_count+1
                        if space_count%2==0:
                            html_data+="""<br><br><br><br><br><br><br>"""
                        html_data+="""<div><br><br><br><br><br>
                        <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                            <div class="row">
                                                <div class="col-sm-6 col-xs-6" >
                                                    <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                                </div>
                                                <div class="col-sm-6 col-xs-6"><div>

                                                  <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                    <thead>
                                                      <tr>
                                                        <td><b>#</b></td>

                                                        <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>
                                                        <td align="right"><b>"""+str_key1+"""</b></td>"""
                        if str_type.upper() == 'SALE' or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == ' LMS STAFF REPORT' or  str_report.upper() == " LMS BRANCH REPORT":
                            html_data += """<td align="right"><b>"""+str_key2+"""</b></td>"""
                        html_data+="""</tr>
                                                    </thead>
                                                    <tbody>
                                                      """+dct_details[details.split('-')[0]][4]+"""
                                                    </tbody>
                                                  </table></div>
                                                </div>
                                            </div>
                                          </div>"""
                    elif str_report == 'Feedback Report':
                        int_cont +=1
                        space_count=space_count+1
                        if space_count%2==0:
                            html_data+="""<br><br><br><br><br><br><br>"""
                        html_data+="""<div><br><br><br><br><br>
                                            <div class="row">
                                                <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                                <div class="col-sm-6 col-xs-6" >
                                                    <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                                </div>
                                                <div class="col-sm-6 col-xs-6"><div>

                                                  <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                    <thead>
                                                      <tr>
                                                        <td><b>#</b></td>

                                                        <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>
                                                        <td align="right"><b>Rating</b></td>
                                                      </tr>
                                                    </thead>
                                                    <tbody>
                                                      """+dct_details[details.split('-')[0]][3]+"""
                                                    </tbody>
                                                  </table></div>
                                                </div>
                                            </div>
                                          </div>"""
                    else:
                        space_count=space_count+1
                        if space_count%2==0:
                            html_data+="""<br><br><br><br><br><br><br>"""
                        html_data+="""<div><br><br><br><br><br>
                                            <div class="row">
                                                <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                                <div class="col-sm-6 col-xs-6" >
                                                    <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                                </div>
                                                <div class="col-sm-6 col-xs-6"><div>

                                                  <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                    <thead>
                                                      <tr>
                                                        <td><b>#</b></td>

                                                        <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>
                                                        <td align="right"><b>"""+str_data_name+"""</b></td>
                                                      </tr>
                                                    </thead>
                                                    <tbody>
                                                      """+dct_details[details.split('-')[0]][3]+"""
                                                    </tbody>
                                                  </table></div>
                                                </div>
                                            </div>
                                          </div>"""
                elif details.split('-')[1].upper() =='PIE':
                    space_count=space_count+1
                    if space_count%2==0:
                        html_data+="""<br><br><br><br><br><br><br>"""
                    html_data+="""<div><br><br><br><br><br>
                                    <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                        <div class="row">
                                            <div class="col-sm-6 col-xs-6" >
                                                <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                            </div>
                                            <div class="col-sm-6 col-xs-6"><div>

                                              <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                <thead>
                                                  <tr>
                                                    <td><b>#</b></td>

                                                    <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>"""
                    if str_type.upper() == 'SALE':
                        html_data+="""<td><b>Sale</b></td>"""
                    elif str_report == 'Feedback Report':
                        html_data+="""<td><b>Count</b></td>"""
                    else:
                        html_data+="""<td><b>Enquiry</b></td>"""
                    html_data+="""</tr>
                                                </thead>
                                                <tbody>
                                                  """+dct_details[details.split('-')[0]][1]+"""
                                                </tbody>
                                              </table></div>
                                            </div>
                                        </div>
                                      </div>"""
            html_data+="""</div></body>
                             <script>"""
            # HTML FOR BAR AND PIE CHART
            for details in lst_details:
                if details.split('-')[1].upper() =='BAR':
                    if not str_report == 'NA Enquiry Report':
                        html_data+="""
                        var """+details.split('-')[0]+""" = c3.generate({
                        bindto:'#"""+details.split('-')[0]+"""',
                        data: {
                        x : 'x',"""
                        if str_type.upper() == "SALE" or str_report.upper() == " LMS TOP VIEWED REPORT" or str_report.upper() == " LMS STAFF REPORT" or  str_report.upper() == " LMS BRANCH REPORT":
                            html_data+="""columns: ["""+str(dct_details[details.split('-')[0]][1])+""","""+str(dct_details[details.split('-')[0]][2])+""","""+str(dct_details[details.split('-')[0]][3])+"""
                            ],"""
                        else:
                            print(dct_details)
                            html_data+="""columns: ["""+str(dct_details[details.split('-')[0]][1])+""","""+str(dct_details[details.split('-')[0]][2])+"""],"""
                        html_data+="""type: 'bar'
                        },
                        axis: {
                        x: {
                        type: 'category'
                        }
                        },
                        color: {
                        pattern: """+str(lst_color)+"""
                        },
                        bar: {
                        width: 15
                        }
                        });"""
                    else:
                        html_data+="""
                        var """+details.split('-')[0]+""" = c3.generate({
                        bindto:'#"""+details.split('-')[0]+"""',
                        data: {
                        x : 'x',
                        columns: ["""+str(dct_details[details.split('-')[0]][1])+""","""+str(dct_details[details.split('-')[0]][2])+"""
                        ],
                        type: 'bar'
                        },
                        axis: {
                        x: {
                        type: 'category'
                        }
                        },
                        color: {
                        pattern: """+str(lst_color)+"""
                        },
                        bar: {
                        width: 15
                        }
                        });"""
                elif details.split('-')[1].upper() =='PIE':
                    html_data+="""
                                    var"""+details.split('-')[0]+""" = c3.generate({
                       bindto: '#"""+details.split('-')[0]+"""',
                       data: {
                           columns:
                               """+str(dct_pie_details[details.split('-')[0]])+"""
                           ,
                           type: 'pie'
                       },"""
                    if pie_chart_colour:
                        html_data+="""color: {
                                pattern: """+str(pie_chart_colour)+"""
                                },"""
                    html_data+="""bar: {
                                   width: 15
                               }
                             });"""
            html_data+=""" </script>
                            </html>"""
            filename =  'Report.pdf'
            options = {
                                'page-size': 'A4',
                                'margin-top': '10.00mm',
                                'margin-right': '10.00mm',
                                'margin-bottom': '10.00mm',
                                'margin-left': '10.00mm',
                                'dpi':400,
                            }
            # import pdb; pdb.set_trace()
            pdfkit.from_string(html_data,pdf_path+filename, options=options)
            lst_file.append(filename)

        # TABLE GENERATION
        if request.data['bln_table']:
            # IN THE CASE OF NO CHART
            if not request.data['bln_chart']:
                lst_tbl_head = lst_details
                lst_tbl_index = dct_label
                dct_table_data = dct_data
            if request.data['report_type']:
                html_data = """<!DOCTYPE HTML>
                                <html>
                                <head>
                                    <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>
                                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                                </head>
                                <body style="font-family: sans-serif; font-size: 14px;">
                                  <div style="width:1000px; height:100%; margin:0 auto; padding:0px 30px; float:center; border:1px solid #000;">

                                      <h3 class="text-center"><b>"""+str_report+"""</b></h4>

                                        <div class="row" style="padding:15px;">
                                          <div class="col-sm-7 col-xs-7">
                                            <div class="row"><div class="col-sm-3 col-xs-3"><b>From</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                            <div class="row"><div class="col-sm-3 col-xs-3"><b>To</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                            <div class="row"><div class="col-sm-3 col-xs-3"><b>Taken By</b></div><div class="col-sm-9 col-xs-9">"""+request.user.first_name+" "+request.user.last_name+"""</div></div>
                                          </div>
                                          <div class="col-sm-5 col-xs-5">"""
                if request.data.get('branch') or request.data.get('branchselected'):

                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b> </div><div class="col-sm-7 col-xs-7">"""+str_branch+"""</div></div>"""
                else:
                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b></div><div class="col-sm-7 col-xs-7">All</div></div>"""
                if request.data.get('staff') or request.data.get('staffs'):
                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">"""+str_staff+"""</div></div>"""

                if request.data.get('custselected'):
                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Customer</b> </div><div class="col-sm-7 col-xs-7">"""+str_cust+"""</div></div>"""
                html_data+="""<div class="row"><div class="col-sm-5 col-xs-5"><b>Action Date</b></div><div class="col-sm-7 col-xs-7"><span>"""+datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p")+"""</span></div></div></div></div>
                <div style="padding-top:20px">
                    <table class="table">
                        <thead>
                            <tr class="row" >"""
                for str_tbl_head in lst_tbl_head:
                    if str_tbl_head.upper() == 'ENQUIRY NO':
                        html_data += """<th width="12%">"""+str_tbl_head+"""</th>"""
                    else:
                        html_data += """<th>"""+str_tbl_head+"""</th>"""
                html_data +="""</tr>
                        </thead>
                        <tbody>"""
                for table in dct_table_data:
                    html_data +='''<tr class="row">'''
                    for int_index in lst_tbl_index:
                        if lst_tbl_index.index(int_index) == 0:
                            html_data += '''<td width="12%">'''+str(table[int_index])+'''</td>'''
                        else:
                            html_data += '''<td>'''+str(table[int_index])+'''</td>'''
                    html_data +='''</tr>'''
                html_data+='''</tbody>
                    </div>
                    </main>
                  </div>
                 </body>
                 <script>
                 </script>
                </html>
                '''
                filename = 'TableData.pdf'
                options = {
                                    'page-size': 'A4',
                                    'margin-top': '10.00mm',
                                    'margin-right': '10.00mm',
                                    'margin-bottom': '10.00mm',
                                    'margin-left': '10.00mm',
                                    'dpi':200,
                                }
                pdfkit.from_string(html_data,pdf_path+filename, options=options)
                lst_file.append(filename)
        # DOWNLOAD
        if request.data.get('export_type').upper() == 'DOWNLOAD':
            fs = FileSystemStorage()
            lst_encoded_string=[]
            for filename in lst_file:
                if fs.exists(pdf_path+filename):
                    with fs.open(pdf_path+filename) as pdf:
                        lst_encoded_string.append(str(base64.b64encode(pdf.read())))
            file_details = {}
            file_details['file'] = lst_encoded_string
            file_details['file_name'] = lst_file
            return file_details
        elif request.data.get('export_type').upper() == 'MAIL':
            to = request.data.get('email').split(",")
            subject =  str_report
            from_email = settings.EMAIL_HOST_EMAIL
            text_content = 'Travidux'
            html_content = '''Dear '''
            mail = EmailMultiAlternatives(subject, text_content, from_email, to)
            mail.attach_alternative(html_content, "text/html")
            for file in lst_file:
                mail.attach_file(pdf_path+file)
                remove(pdf_path+file)
            mail.send()
            return Response({'status': 1})
    except Exception as e:
        ins_logger.logger.error(str(e))
        return Response({'status':'0','data':str(e)})



def general_generate_pdf(request,str_report,lst_details=None,dct_label=None,dct_data=None,lst_tbl_head=None,lst_tbl_index=None,dct_table_data=None):
    space_count=1
    """
    used to generate pdf of general reports
    parameter : request,report name,chart details,table details
    return: file name
    """
    try:
        str_data_name = 'Enquiry'
        if request.data['reportname'] in ['branch_profit_report','territory_profit_report','product_profit_report','zone_profit_report','item_profit_report','price_range_profit_report']:
            str_data_name = 'Profit'
        elif(request.data['reportname'] in ['reward_summary_report','reward_zone_report','reward_territory_report','reward_branch_report','reward_staff_report']):
            str_data_name = 'Reward'
        lst_file=[]
        pie_chart_colour = []
        # chart colour from admin settings

        if AdminSettings.objects.filter(fk_company=1,vchr_code='SALES_COLOUR',bln_enabled=True).exists():
            sale_color = AdminSettings.objects.get(fk_company=1,vchr_code='SALES_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            sale_color = '#1f77b4'
        if AdminSettings.objects.filter(fk_company=1,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).exists():
            enquiry_color = AdminSettings.objects.get(fk_company=1,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).vchr_value[0]
        else:
            enquiry_color='#aec7e8'

        lst_color=[enquiry_color,sale_color]
        if AdminSettings.objects.filter(fk_company=1,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).exists():
            pie_chart_colour = AdminSettings.objects.get(fk_company=1,vchr_code='PIE_CHART_COLOURS',bln_enabled=True).vchr_value

        # branch filter-branch name
        if request.data.get('branchselected'):
            str_branch = list(Branch.objects.filter(pk_bint_id__in= request.data.get('branchselected')).values('vchr_name'))[0]['vchr_name']

        # staff filter-staff name
        if request.data.get('staffselected'):
            lst_staff =[]
            staff_id = request.data.get('staffstaffselected',[])
            rst_staff = list(User.objects.filter(id__in=lst_staff).values('first_name','last_name'))
            str_staff = ''
            if rst_staff:
                for ins_staff in rst_staff:
                    str_staff += ins_staff['first_name'].title()+' '+ins_staff['last_name'].title()+'  ,'
                str_staff = str_staff.rsplit(' ', 2)[0]

        # customer filter - customer name
        if request.data.get('custselected'):
            rst_customer = list(CustomerModel.objects.filter(cust_mobile__in=request.data.get('custselected',[])).values('cust_fname','cust_lname'))
            str_cust = ''
            for ins_cust in rst_customer:
                str_cust +=ins_cust['cust_fname'].title()+' '+ins_cust['cust_lname'].title()+'  ,'
            str_cust = str_cust.rsplit(' ', 2)[0]

        pdf_path = settings.MEDIA_ROOT+'/' #path to save
        lst_status_all = []
        lst_status_all_show = []
        # chart generation
        # import pdb;pdb.set_trace()
        if request.data['bln_chart']:

            dct_details={}
            dct_pie_details = {}
            lst_pie_data = []
            for details in lst_details:
                if details.split('-')[1].upper() =='BAR' or details.split('-')[1].upper() =='GROUPED_BAR': # DATA TO BAR CHART
                    if str_report == 'NA Enquiry Report': # NA ENQUIRY BAR CHART
                        lst_item = ['x']
                        lst_name = [details.split('-')[0]]
                        tbl_data =''
                        i=1
                        for item in dct_data[details.split('-')[0]][1]:
                            name=''
                            if details=='staff_all':# IN STAFF,STAFF CODE CHANGE TO STAFF NAME
                                name=dct_data['staffs'][item]
                            else:
                                name=item
                            if len(name)>31:
                                str_name=name[:29]+"..."
                            else:
                                str_name=name
                            lst_item.append(i)
                            lst_name.append(int(dct_data[details.split('-')[0]][1][item]))
                            # TABLE DATA TO DISPLAY RIGHT SIDE OF CHART
                            tbl_data+='<tr><td>'+str(i)+'</td><td>'+str(str_name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][1][item])+'</td></tr>'
                            i+=1
                            dct_details[details.split('-')[0]]=[dct_label[details.split('-')[0]],lst_item,lst_name,tbl_data]
                    else:#BAR CHART OF ALL OTHER REPORTS
                        lst_item = ['x']
                        lst_enquiry = [str_data_name]
                        lst_sale = ['Sale']
                        tbl_data =''
                        i=0

                        for item in dct_data[details.split('-')[0]]:
                            name=''
                            if details.split('-')[0] =='staff_all':
                                name=dct_data['staffs'][item]
                            else:
                                name=list(item.keys())[0]
                            if len(name)>31:
                                str_name=name[:29]+"..."
                            else:
                                str_name=name
                            lst_item.append(i+1)
                            lst_enquiry.append(int(dct_data[details.split('-')[0]][i][name]['Value1']))
                            lst_sale.append(int(dct_data[details.split('-')[0]][i][name]['Value2']))
                            if request.data['report_type'].upper() == 'SALE':
                                tbl_data+='<tr><td>'+str(i+1)+'</td><td>'+str(str_name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][i][name]['Value1'])+'</td><td align="right">'+str(dct_data[details.split('-')[0]][i][name]['Value2'])+'</td></tr>'
                            else:
                                tbl_data+='<tr><td>'+str(i+1)+'</td><td>'+str(str_name)+'</td><td align="right">'+str(dct_data[details.split('-')[0]][i][name]['Value1'])+'</td></tr>'
                            i+=1
                            dct_details[details.split('-')[0]]=[dct_label[details.split('-')[0]],lst_item,lst_enquiry,lst_sale,tbl_data]
                elif details.split('-')[1].upper() =='PIE': #DATA TO GENERATE PIE CHART
                    int_no = 1
                    str_key = 'Value1'
                    str_status = ''
                    if request.data['report_type']=='Sale':
                        str_key = 'Value1'

                    dct_pie_details[details.split('-')[0]] = []
                    for str_data in dct_data[details.split('-')[0]]:
                        if not type(dct_data[details.split('-')[0]][str_data]) == type(1):
                            if details.split('-')[0] =='staff_all':
                                name=dct_data['staffs'][str_data]
                            else:
                                name=str_data

                            lst_status_all.append(dct_label[details.split('-')[0]])
                            lst_pie_data.append(name)
                            lst_pie_data.append(str(dct_data[details.split('-')[0]][str_data][str_key]))
                            dct_pie_details[details.split('-')[0]].append(list(lst_pie_data))
                            str_status += '''<tr><td>'''+str(int_no)+'''</td><td>'''+str(name)+'''</td><td>'''+str(dct_data[details.split('-')[0]][str_data][str_key])+'''</td></tr>'''
                            lst_status_all.append(str_status)
                            lst_status_all_show = lst_status_all
                            dct_details[details.split('-')[0]] = lst_status_all_show
                            lst_pie_data = []
                            lst_status_all = []
                            lst_status_all_show = []
                            int_no +=1
                        else:
                            if details.split('-')[0] =='staff_all':
                                name=dct_data['staffs'][str_data]
                            else:
                                name=str_data
                            lst_status_all.append(dct_label[details.split('-')[0]])
                            lst_pie_data.append(name)
                            lst_pie_data.append(str(dct_data[details.split('-')[0]][str_data]))
                            dct_pie_details[details.split('-')[0]].append(list(lst_pie_data))

                            str_status += '''<tr><td>'''+str(int_no)+'''</td><td>'''+str(name)+'''</td><td>'''+str(dct_data[details.split('-')[0]][str_data])+'''</td></tr>'''
                            lst_status_all.append(str_status)
                            lst_status_all_show = lst_status_all
                            dct_details[details.split('-')[0]] = lst_status_all_show
                            lst_pie_data = []
                            lst_status_all = []
                            lst_status_all_show = []
                            int_no +=1
            #HTML FOR TABLE CORRESPONDING CHART
            html_data = """<!DOCTYPE HTML>
                            <html>
                            <head>
                                <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>
                                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                            </head>
                            <body style="font-family: sans-serif; font-size: 14px;">
                              <div style="width:1000px; height:100%; margin:0 auto; padding:0px 30px; float:center; border:1px solid #000;">
                                  <br>
                                  <h3 class="text-center"><b style="color:#31708f !important;">"""+str_report+"""</b></h3>
                                  <br>
                                    <div class="row" style="padding:15px;">
                                      <div class="col-sm-7 col-xs-7">
                                        <div class="row"><div class="col-sm-3 col-xs-3"><b>From</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                        <div class="row"><div class="col-sm-3 col-xs-3"><b>To</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                        <div class="row"><div class="col-sm-3 col-xs-3"><b>Taken By</b></div><div class="col-sm-9 col-xs-9">"""+request.user.first_name+" "+request.user.last_name+"""</div></div>
                                      </div>
                                      <div class="col-sm-5 col-xs-5">"""
            if request.data.get('branch') or request.data.get('branchselected'):
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b> </div><div class="col-sm-7 col-xs-7">"""+str_branch+"""</div></div>"""
            else:
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b></div><div class="col-sm-7 col-xs-7">All</div></div>"""
            if request.data.get('staff') or request.data.get('staffs'):
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">"""+str_staff+"""</div></div>"""
            # else:
            #     html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">All</div></div>"""
            if request.data.get('custselected'):
                html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Customer</b> </div><div class="col-sm-7 col-xs-7">"""+str_cust+"""</div></div>"""
            html_data+="""<div class="row"><div class="col-sm-5 col-xs-5"><b>Action Date</b></div><div class="col-sm-7 col-xs-7"><span>"""+datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p")+"""</span></div></div></div></div><br>"""
            for details in lst_details:

                if details.split('-')[1].upper() =='BAR' or details.split('-')[1].upper() =='GROUPED_BAR' :
                    if not str_report == 'NA Enquiry Report':
                        space_count=space_count+1
                        if space_count%2==0:
                            html_data+="""<br><br><br><br><br><br><br>"""
                        html_data+="""<div><br><br><br><br><br>
                                            <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                            <div class="row">
                                                <div class="col-sm-6 col-xs-6" >
                                                    <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                                </div>
                                                <div class="col-sm-6 col-xs-6"><div>

                                                  <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                    <thead>
                                                      <tr>
                                                        <td><b>#</b></td>
                                                        <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>
                                                        <td align="right"><b>"""+str_data_name+"""</b></td>"""
                        if request.data['report_type'].upper() == 'SALE':
                            html_data += """<td align="right"><b>Sale</b></td>"""
                        html_data+="""</tr>
                                                    </thead>
                                                    <tbody>
                                                      """+dct_details[details.split('-')[0]][4]+"""
                                                    </tbody>
                                                  </table></div>
                                                </div>
                                            </div>
                                          </div>"""
                    else:
                        space_count=space_count+1
                        if space_count%2==0:
                            html_data+="""<br><br><br><br><br><br><br>"""
                        html_data+="""<div><br><br><br><br><br>
                                            <div class="row">
                                                <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                                <div class="col-sm-6 col-xs-6" >
                                                    <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                                </div>
                                                <div class="col-sm-6 col-xs-6"><div>
                                                  <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                    <thead>
                                                      <tr>
                                                        <td><b>#</b></td>
                                                        <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>
                                                        <td align="right"><b>"""+str_data_name+"""</b></td>
                                                      </tr>
                                                    </thead>
                                                    <tbody>
                                                      """+dct_details[details.split('-')[0]][3]+"""
                                                    </tbody>
                                                  </table></div>
                                                </div>
                                            </div>
                                          </div>"""
                elif details.split('-')[1].upper() =='PIE':
                    space_count=space_count+1
                    if space_count%2==0:
                        html_data+="""<br><br><br><br><br><br><br>"""
                    html_data+="""<div><br><br><br><br><br>
                                        <div class="text-center"style="padding:15px;"><b style="color:#31708f !important;">"""+dct_details[details.split('-')[0]][0].upper()+"""</b></div>
                                        <div class="row">
                                            <div class="col-sm-6 col-xs-6" >
                                                <div id='"""+details.split('-')[0]+"""' style="height:370px;"></div>
                                            </div>
                                            <div class="col-sm-6 col-xs-6"><div>
                                              <table class="table" style="padding-top:25px;padding-bottom:25px;">
                                                <thead>
                                                  <tr>
                                                    <td><b>#</b></td>
                                                    <td><b>"""+dct_details[details.split('-')[0]][0].rstrip("wise")+"""</b></td>"""
                    if request.data['report_type'].upper() == 'SALE':
                        html_data+="""<td><b>Sale</b></td>"""
                    else:
                        html_data+="""<td><b>"""+str_data_name+"""</b></td>"""
                    html_data+="""</tr>
                                                </thead>
                                                <tbody>
                                                  """+dct_details[details.split('-')[0]][1]+"""
                                                </tbody>
                                              </table></div>
                                            </div>
                                        </div>
                                      </div>"""
            html_data+="""</div></body>
                             <script>"""
            # HTML FOR BAR AND PIE CHART
            for details in lst_details:

                if details.split('-')[1].upper() =='BAR' or details.split('-')[1].upper() =='GROUPED_BAR':
                    if not str_report == 'NA Enquiry Report':
                        html_data+="""
                        var """+details.split('-')[0]+""" = c3.generate({
                        bindto:'#"""+details.split('-')[0]+"""',
                        data: {
                        x : 'x',"""
                        if request.data['report_type'].upper() == "SALE":
                            html_data+="""columns: ["""+str(dct_details[details.split('-')[0]][1])+""","""+str(dct_details[details.split('-')[0]][2])+""","""+str(dct_details[details.split('-')[0]][3])+"""
                            ],"""
                        else:
                            html_data+="""columns: ["""+str(dct_details[details.split('-')[0]][1])+""","""+str(dct_details[details.split('-')[0]][2])+"""],"""
                        html_data+="""type: 'bar'
                        },
                        axis: {
                        x: {
                        type: 'category'
                        }
                        },
                        color: {
                        pattern: """+str(lst_color)+"""
                        },
                        bar: {
                        width: 15
                        }
                        });"""
                    else:
                        html_data+="""
                        var """+details.split('-')[0]+""" = c3.generate({
                        bindto:'#"""+details.split('-')[0]+"""',
                        data: {
                        x : 'x',
                        columns: ["""+str(dct_details[details.split('-')[0]][1])+""","""+str(dct_details[details.split('-')[0]][2])+"""
                        ],
                        type: 'bar'
                        },
                        axis: {
                        x: {
                        type: 'category'
                        }
                        },
                        color: {
                        pattern: """+str(lst_color)+"""
                        },
                        bar: {
                        width: 15
                        }
                        });"""
                elif details.split('-')[1].upper() =='PIE':
                    html_data+="""
                                    var"""+details.split('-')[0]+""" = c3.generate({
                       bindto: '#"""+details.split('-')[0]+"""',
                       data: {
                           columns:
                               """+str(dct_pie_details[details.split('-')[0]])+"""
                           ,
                           type: 'pie'
                       },"""
                    if pie_chart_colour:
                        html_data+="""color: {
                                pattern: """+str(pie_chart_colour)+"""
                                },"""
                    html_data+="""bar: {
                                   width: 15
                               }
                             });"""
            html_data+=""" </script>
                            </html>"""
            filename =  'Report.pdf'
            options = {
                                'page-size': 'A4',
                                'margin-top': '10.00mm',
                                'margin-right': '10.00mm',
                                'margin-bottom': '10.00mm',
                                'margin-left': '10.00mm',
                                'dpi':400,
                            }
            pdfkit.from_string(html_data,pdf_path+filename, options=options)
            lst_file.append(filename)

        # TABLE GENERATION
        if request.data['bln_table']:
            # IN THE CASE OF NO CHART
            if not request.data['bln_chart']:
                lst_tbl_head = lst_details
                lst_tbl_index = dct_label
                dct_table_data = dct_data
            if request.data['report_type']:
                html_data = """<!DOCTYPE HTML>
                                <html>
                                <head>
                                    <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>
                                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                                </head>
                                <body style="font-family: sans-serif; font-size: 14px;">
                                  <div style="width:1000px; height:100%; margin:0 auto; padding:0px 30px; float:center; border:1px solid #000;">

                                      <h3 class="text-center"><b>"""+str_report+"""</b></h4>

                                        <div class="row" style="padding:15px;">
                                          <div class="col-sm-7 col-xs-7">
                                            <div class="row"><div class="col-sm-3 col-xs-3"><b>From</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                            <div class="row"><div class="col-sm-3 col-xs-3"><b>To</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
                                            <div class="row"><div class="col-sm-3 col-xs-3"><b>Taken By</b></div><div class="col-sm-9 col-xs-9">"""+request.user.first_name+" "+request.user.last_name+"""</div></div>
                                          </div>
                                          <div class="col-sm-5 col-xs-5">"""
                if request.data.get('branch') or request.data.get('branchselected'):

                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b> </div><div class="col-sm-7 col-xs-7">"""+str_branch+"""</div></div>"""
                else:
                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b></div><div class="col-sm-7 col-xs-7">All</div></div>"""
                if request.data.get('staff') or request.data.get('staffs'):
                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">"""+str_staff+"""</div></div>"""

                if request.data.get('custselected'):
                    html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Customer</b> </div><div class="col-sm-7 col-xs-7">"""+str_cust+"""</div></div>"""
                html_data+="""<div class="row"><div class="col-sm-5 col-xs-5"><b>Action Date</b></div><div class="col-sm-7 col-xs-7"><span>"""+datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p")+"""</span></div></div></div></div>
                <div style="padding-top:20px">
                    <table class="table">
                        <thead>
                            <tr class="row" >"""
                for str_tbl_head in lst_tbl_head:
                    if str_tbl_head.upper() == 'ENQUIRY NO':
                        html_data += """<th width="12%">"""+str_tbl_head+"""</th>"""
                    else:
                        html_data += """<th>"""+str_tbl_head+"""</th>"""
                html_data +="""</tr>
                        </thead>
                        <tbody>"""
                for table in dct_table_data:
                    html_data +='''<tr class="row">'''
                    for int_index in lst_tbl_index:
                        if lst_tbl_index.index(int_index) == 0:
                            html_data += '''<td width="12%">'''+str(table[int_index])+'''</td>'''
                        else:
                            html_data += '''<td>'''+str(table[int_index])+'''</td>'''
                    html_data +='''</tr>'''
                html_data+='''</tbody>
                    </div>
                    </main>
                  </div>
                 </body>
                 <script>
                 </script>
                </html>
                '''
                filename = 'TableData.pdf'
                options = {
                                    'page-size': 'A4',
                                    'margin-top': '10.00mm',
                                    'margin-right': '10.00mm',
                                    'margin-bottom': '10.00mm',
                                    'margin-left': '10.00mm',
                                    'dpi':200,
                                }
                pdfkit.from_string(html_data,pdf_path+filename, options=options)
                lst_file.append(filename)
        # DOWNLOAD
        if request.data.get('export_type').upper() == 'DOWNLOAD':
            fs = FileSystemStorage()
            lst_encoded_string=[]
            for filename in lst_file:
                if fs.exists(pdf_path+filename):
                    with fs.open(pdf_path+filename) as pdf:
                        lst_encoded_string.append(str(base64.b64encode(pdf.read())))
            file_details = {}
            file_details['file'] = lst_encoded_string
            file_details['file_name'] = lst_file
            return file_details
        elif request.data.get('export_type').upper() == 'MAIL':
            to = request.data.get('email').split(",")
            subject =  str_report
            from_email = settings.EMAIL_HOST_EMAIL
            text_content = 'Travidux'
            html_content = '''Dear '''
            mail = EmailMultiAlternatives(subject, text_content, from_email, to)
            mail.attach_alternative(html_content, "text/html")
            for file in lst_file:
                mail.attach_file(pdf_path+file)
                remove(pdf_path+file)
            mail.send()
            return Response({'status': 1})
    except Exception as e:
        ins_logger.logger.error(str(e))
        return Response({'status':'0','data':str(e)})
