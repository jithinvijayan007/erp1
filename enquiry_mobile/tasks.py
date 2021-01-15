# from __future__ import absolute_import
# from celery import shared_task
# # from reports import generate_report_excel


# import pyqrcode
# import png

# from django.shortcuts import render
# from django.core.urlresolvers import reverse_lazy
# from django.views import generic
# from django.http import JsonResponse
# from rest_framework import generics
# from rest_framework.views import APIView
# from rest_framework import permissions
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from django.http import HttpResponseRedirect, HttpResponse
# from django.core.files.storage import FileSystemStorage
# from rest_framework.response import Response
# from rest_framework import viewsets
# from company.models import CompanyDetails
# from customer_app.models import CustomerModel
# from enquiry.models import EnquiryMaster,Flights,Hotel,Package,Visa,TravelInsurance,Forex,Transport,Other, Train
# from software.models import EnquiryTrack,AccountingSoftware,HrSolutions,EmployeeManagement
# from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry,ItemEnquiry
# from auto_mobile.models import SuvEnquiry,SedanEnquiry,HatchbackEnquiry
# from kct_package.models import Kct,KctPackage
# from branch.models import Branch
# from user_app.models import UserModel
# from hasher.views import hash_enquiry
# from os import path,makedirs,remove,listdir
# import pdfkit
# import base64
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# import math
# from django.core.mail import EmailMultiAlternatives
# from CRM import ins_logger
# from adminsettings.models import AdminSettings
# from enquiry.models import EnquiryMaster
# from CRM import settings
# import requests


# @shared_task # Use this decorator to make this a asyncronous function
# def send_feedback_sms(int_enq_master_id):
#     try:
#         if AdminSettings.objects.filter(vchr_code = 'staff_rating_sms').values('bln_enabled').first()['bln_enabled'] == True:
#             ins_enquiry = EnquiryMaster.objects.filter(pk_bint_id=int_enq_master_id).values("pk_bint_id","vchr_hash","fk_customer__cust_mobile").order_by('-pk_bint_id')
#             staffurl =settings.HOSTNAME+"/invoice_feedback/"+ins_enquiry[0]['vchr_hash']
#             int_customer_phone = ins_enquiry[0]['fk_customer__cust_mobile']
#             rsp_request=requests.get("https://app.smsbits.in/api/users?id=OTg0NjY2OTk1NQ&senderid=myGsms&to="+str(int_customer_phone)+"&msg=Dear Customer, Thank you for your presence in myG. Please click here to provide your valuable feedback for improving our service. "+staffurl+"&port=TA")
#             return {"status": True}
#         return {"status": False}
#     except Exception as e:
#         print(str(e))
#         return True


# @shared_task
# def print_fun():
#     print("email sent successfully")

# @shared_task
# def email_sent(subject, text_content, from_email,to,html_content,filename):
#     # time.sleep(100)
#     mail = EmailMultiAlternatives(subject, text_content, from_email, [to])
#     mail.attach_alternative(html_content, "text/html")
#     mail.attach_file(filename)
#     mail.send()
#     remove(filename)
#     print("email-now")

# # @shared_task  # Use this decorator to make this a asyncronous function
# # def enquiry_print(enquiry_no,request,ins_user):
# #     try:
# #         import pdb; pdb.set_trace()
# #         ins_company = CompanyDetails.objects.filter(pk_bint_id = ins_user.fk_company.pk_bint_id).values().order_by('-pk_bint_id')
# #         ins_enquiry = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company_id = ins_company[0]['pk_bint_id'],vchr_enquiry_num = enquiry_no).values().order_by('-pk_bint_id')
# #         ins_customer = CustomerModel.objects.filter(fk_company_id = ins_company[0]['pk_bint_id'],id = ins_enquiry[0]['fk_customer_id']).values().order_by('-id')
# #         # ins_branch = Branch.objects.filter(fk_company_id = ins_company[0]['pk_bint_id']).values().order_by('-pk_bint_id')
# #         ins_branch = Branch.objects.filter(pk_bint_id = request.user.usermodel.fk_branch_id).values().order_by('-pk_bint_id')
# #         images = settings.HOSTNAME+'/static/'+ins_company[0]['vchr_logo']
# #         # createing qr code shafeer
# #         url_qr_code = pyqrcode.create(settings.HOSTNAME+"view_enquiry/"+ins_enquiry[0]['vchr_hash'])
# #         url_qr_code.png(settings.STATIC_DIR+'/'+ins_enquiry[0]['vchr_enquiry_num']+'.png', scale=6)
# #         qrcodePath = settings.STATIC_DIR+'/'+ins_enquiry[0]['vchr_enquiry_num']+'.png'
# #         bln_send_mail = True
# #         str_html = """
# #         <!DOCTYPE html>
# #         <html>
# #         <head>
# #         <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
# #         <title>Travidux Enquiry</title>
# #         <style type="text/css">
# #         body {
# #             margin-left: 0px;
# #             margin-top: 0px;
# #             margin-right: 0px;
# #             margin-bottom: 0px;
# #             font-family: sans-serif;
# #             font-size: 20px;
# #             /*background: #f3f3f3;*/
# #         }
# #         </style>
# #         </head>
# #         <body>
# #         <!--.main_warper_start-->
# #
# #
# #           <table width="100%" border="0" cellspacing="0" cellpadding="0" background="#000" bordercolor="#000000" style="font-weight:400; margin-top:-10px">
# #             <tr>
# #               <td style="width:50%;"><div style="width:96%; float:left; padding:10px; text-align:left; font-size:20px;">
# #                   <p style="margin:14px 0; color:#000; text-transform:uppercase; color:#696a6b;">Bill To<strong style="color:#000; display:block; text-transform:capitalize;">"""+ins_customer[0]['cust_salutation']+""". """+ins_customer[0]['cust_fname']+""" """+ins_customer[0]['cust_lname']+"""</strong></p>
# #                   <p style="margin:10px 0; color:#696a6b;">"""+str(ins_customer[0]['cust_mobile'])+"""</span></p>
# #                   <p style="margin:0; color:#696a6b;">"""+ins_customer[0]['cust_email']+"""</p>
# #                 </div></td>
# #               <td><div style="width:96%; padding:10px; text-align:right; font-size:20px;">
# #                   <p style="margin:14px 0; color:#000;">Enquiry Number :<span style="margin:0 0 0 5px; display:inline-block; width:210px; text-align:right;"><strong>"""+ins_enquiry[0]['vchr_enquiry_num']+"""</strong></span></p>
# #                   <p style="margin:14px 0; color:#000;">Enquiry Date :<span style="margin:0 0 0 5px; display:inline-block; width:210px; text-align:right;"><strong>"""+str(ins_enquiry[0]['dat_created_at'].strftime("%d-%m-%Y"))+"""</strong></span></p>
# #                   <p style="margin:14px 0; color:#000;">GST :<span style="margin:0 0 0 5px; display:inline-block; width:210px; text-align:right;"><strong>"""+ins_company[0]['vchr_gst']+"""</strong></span></p>
# #                   <p style="margin:14px 0; color:#000;">Branch :<span style="margin:0 0 0 5px; display:inline-block; width:210px; text-align:right;"><strong>"""+str(ins_branch[0]['vchr_name']).title()+"""</strong></span></p>
# #                 </div></td>
# #             </tr>
# #           </table>
# #            <table width="100%" border="0" cellspacing="0" cellpadding="0" background="#000" style="margin:0; background:#fff; border:0;  border-bottom: 1px solid #e2e2e2;" bordercolor="#000000">
# #             <tr style="background:#4a4a4a; color:#FFF; font-weight:600; font-size:17px;">
# #               <td width="30%" style="padding:13px;">Items</td>
# #               <td width="50%"style="padding:13px;">Description</td>
# #               <td width="20%" align="right" style="padding:13px;">Estimated Amount</td>
# #             </tr>
# #          """
# #
# #         flt_total = 0
# #         if ins_user.fk_company.fk_company_type.vchr_company_type == 'TRAVEL AND TOURISM':
# #             ins_flight = Flights.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_source_id__vchr_iata_code','fk_destination_id__vchr_iata_code','dat_departure', 'dbl_estimated_amount','vchr_enquiry_status')
# #             ins_train = Train.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_source_id__vchr_code','fk_destination_id__vchr_code','dat_departure', 'dbl_estimated_amount','vchr_enquiry_status')
# #             ins_hotel = Hotel.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('dat_check_in','dat_check_out','dbl_estimated_amount','int_rooms','vchr_enquiry_status')
# #             ins_package = Package.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('dat_from','dat_to','dbl_estimated_amount','vchr_enquiry_status')
# #             ins_visa = Visa.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('vchr_visa_category','fk_country__vchr_country_name','dbl_estimated_amount','vchr_enquiry_status')
# #             ins_travelinsurance = TravelInsurance.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('dat_from','dat_to','dbl_estimated_amount','vchr_enquiry_status')
# #             ins_forex = Forex.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('vchr_from','vchr_to','dbl_estimated_amount','vchr_enquiry_status')
# #             ins_transport = Transport.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('dat_from','dat_to','dbl_estimated_amount','vchr_enquiry_status')
# #             ins_other = Other.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('dbl_estimated_amount','vchr_enquiry_status')
# #             ins_kct = Kct.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_kct_package_id__vchr_package_name','dat_travel','int_count','dbl_estimated_amount','vchr_enquiry_status')
# #
# #             if ins_kct:
# #                 count = 1
# #             for dct_kct_package in ins_kct:
# #                 flt_amount = dct_kct_package['dbl_estimated_amount']
# #                 if dct_kct_package['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                     bln_send_mail = False
# #                     continue
# #                 if flt_amount != 0:
# #                     str_html += """<tr>
# #                     <td valign="top" style="padding:5px 13px; color:#696a6b;">KCT PACKAGE-"""+str(count)+"""</td>
# #                     <td  valign="top" style="padding:5px 13px; text-align:left;">1  """+dct_kct_package['fk_kct_package_id__vchr_package_name']+""" Package on """+dct_kct_package['dat_travel'].strftime("%d-%m-%Y")+""" with PAX """+dct_kct_package['int_count']+"""</td>
# #                     <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                     </tr>
# #                     """
# #                 count += 1
# #                 flt_total += flt_amount
# #             if ins_flight:
# #                 count = 1
# #                 for dct_flight in ins_flight:
# #                     flt_amount = dct_flight['dbl_estimated_amount']
# #                     if dct_flight['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">FLIGHT-"""+str(count)+"""</td>
# #                         <td  valign="top" style="padding:5px 13px; text-align:left;">1 Ticket from  """+dct_flight['fk_source_id__vchr_iata_code']+""" to """+dct_flight['fk_destination_id__vchr_iata_code']+""" travelling on """+dct_flight['dat_departure'].strftime("%d-%m-%Y")+"""</td>
# #                         <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_train:
# #                 count = 1
# #                 for dct_train in ins_train:
# #                     flt_amount = dct_train['dbl_estimated_amount']
# #                     if dct_train['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">TRAIN-"""+str(count)+"""</td>
# #                         <td  valign="top" style="padding:5px 13px; text-align:left;">1 Ticket from  """+dct_train['fk_source_id__vchr_code']+""" to """+dct_train['fk_destination_id__vchr_code']+""" travelling on """+dct_train['dat_departure'].strftime("%d-%m-%Y")+"""</td>
# #                         <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_visa:
# #                 count = 1
# #                 for dct_visa in ins_visa:
# #                     flt_amount = dct_visa['dbl_estimated_amount']
# #                     if dct_visa['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">VISA-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">1 """+dct_visa['vchr_visa_category']+""" Application to """+dct_visa['fk_country__vchr_country_name']+"""</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_hotel:
# #                 count = 1
# #                 for dct_hotel in ins_hotel:
# #                     flt_amount = dct_hotel['dbl_estimated_amount']
# #                     if dct_hotel['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">HOTEL-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_hotel['int_rooms'])+""" Room from """+dct_hotel['dat_check_in'].strftime("%d-%m-%Y")+""" to """+dct_hotel['dat_check_out'].strftime("%d-%m-%Y")+"""</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_travelinsurance:
# #                 count = 1
# #                 for dct_travelinsurance in ins_travelinsurance:
# #                     flt_amount = dct_travelinsurance['dbl_estimated_amount']
# #                     if dct_travelinsurance['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">TRAVEL INSURANCE-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">1 Travel Insurance from """+dct_travelinsurance['dat_from'].strftime("%d-%m-%Y")+""" to """+dct_travelinsurance['dat_to'].strftime("%d-%m-%Y")+"""</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_forex:
# #                 count = 1
# #                 for dct_forex in ins_forex:
# #                     flt_amount = dct_forex['dbl_estimated_amount']
# #                     if dct_forex['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">FOREX-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">1 From """+dct_forex['vchr_from']+""" to """+dct_forex['vchr_to']+"""</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_transport:
# #                 count = 1
# #                 for dct_transport in ins_transport:
# #                     flt_amount = dct_transport['dbl_estimated_amount']
# #                     if dct_transport['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">TRANSPORT-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">1 from """+dct_transport['dat_from'].strftime("%d-%m-%Y %H:%M")+""" to """+dct_transport['dat_to'].strftime("%d-%m-%Y %H:%M")+"""</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_package:
# #                 count = 1
# #                 for dct_package in ins_package:
# #                     flt_amount = dct_package['dbl_estimated_amount']
# #                     if dct_package['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">PACKAGE-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">1 """+dct_package['dat_from'].strftime("%d-%m-%Y")+""" to """+dct_package['dat_to'].strftime("%d-%m-%Y")+"""</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_other:
# #                 count = 1
# #                 for dct_other in ins_other:
# #                     flt_amount = dct_other['dbl_estimated_amount']
# #                     if dct_other['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                 if flt_amount != 0:
# #                     str_html += """<tr>
# #             <td valign="top" style="padding:5px 13px; color:#696a6b;">OTHER-"""+str(count)+"""</td>
# #             <td  valign="top" style="padding:5px 13px; text-align:left;">1 Other</td>
# #             <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         </tr>
# #         """
# #                     count += 1
# #                     flt_total += flt_amount
# #         #     str_html +="""</table><table width="100%" border="0" cellspacing="0" cellpadding="0" background="#000" style="margin:0;"   bordercolor="#e2e2e2">
# #         # <tr>
# #         # <td style="padding:13px; text-align:right;">&nbsp;</td>
# #         # <td style="padding:13px; text-align:right;"><strong>Total</strong></td>
# #         # <td align="right" style="padding:13px;"><strong>"""+ str(format((math.ceil(flt_total*100)/100),'.2f')) +"""</strong></td>
# #         # </tr>
# #         # </table>
# #         # </div>
# #
# #         # <!--.main_warper_end-->
# #         # </body>
# #         # </html>
# #         #     """
# #         elif ins_user.fk_company.fk_company_type.vchr_company_type == 'SOFTWARE':
# #             ins_enquiry_track = EnquiryTrack.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('int_count','dbl_amount','bln_promo_campaign','bln_digital_marketing','bln_business_intelligence','bln_accounting_software','bln_hr_solutions','bln_employee_management','vchr_enquiry_status')
# #             ins_accounting_software = AccountingSoftware.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('int_count','dbl_amount','bln_promo_campaign','bln_digital_marketing','bln_business_intelligence','bln_enquiry_track','bln_hr_solutions','bln_employee_management','vchr_enquiry_status')
# #             ins_hr_solutions = HrSolutions.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('int_count','dbl_amount','bln_promo_campaign','bln_digital_marketing','bln_business_intelligence','bln_enquiry_track','bln_accounting','bln_employee_management','vchr_enquiry_status')
# #             ins_employee_management = EmployeeManagement.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('int_count','dbl_amount','bln_promo_campaign','bln_digital_marketing','bln_business_intelligence','bln_enquiry_track','bln_accounting','bln_hr_solutions','vchr_enquiry_status')
# #
# #             temp_features = ''
# #             temp_products = ''
# #             # import pdb; pdb.set_trace()
# #             if ins_enquiry_track:
# #                 count = 1
# #                 for dct_enquiry_track in ins_enquiry_track:
# #                     flt_amount = dct_enquiry_track['dbl_amount']
# #                     if dct_enquiry_track['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         temp_features = ''
# #                         temp_products = ''
# #                         if dct_enquiry_track['bln_promo_campaign']:
# #                             temp_features += 'Promo Campaign, '
# #                         if dct_enquiry_track['bln_digital_marketing']:
# #                             temp_features += 'Digital Marketting, '
# #                         if dct_enquiry_track['bln_business_intelligence']:
# #                             temp_features += 'Business Intelligence, '
# #
# #                         if dct_enquiry_track['bln_accounting_software']:
# #                             temp_products += 'Accounting Software, '
# #                         if dct_enquiry_track['bln_hr_solutions']:
# #                             temp_products += 'HR Solutions, '
# #                         if dct_enquiry_track['bln_employee_management']:
# #                             temp_products += 'Employee Management, '
# #
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">Enquiry Track-"""+str(count)+"""</td>
# #                         <td  valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_enquiry_track['int_count'])+""" User </td>
# #                         <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Additional Features</b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td  valign="top" style="padding:5px 13px; text-align:left;">""" + temp_features.strip(', ')+"""</td>
# #                         </tr>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Other Products<b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;">""" + temp_products.strip(', ')+"""</td>
# #                         </tr>
# #                         """
# #                         # <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                     count += 1
# #                     flt_total += flt_amount
# #             if ins_accounting_software:
# #                 count = 1
# #                 for dct_accounting_software in ins_accounting_software:
# #                     flt_amount = dct_accounting_software['dbl_amount']
# #                     if dct_accounting_software['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         temp_features = ''
# #                         temp_products = ''
# #                         if dct_accounting_software['bln_promo_campaign']:
# #                             temp_features += 'Promo Campaign, '
# #                         if dct_accounting_software['bln_digital_marketing']:
# #                             temp_features += 'Digital Marketting, '
# #                         if dct_accounting_software['bln_business_intelligence']:
# #                             temp_features += 'Business Intelligence, '
# #
# #                         if dct_accounting_software['bln_enquiry_track']:
# #                             temp_products += 'Enquiry Track, '
# #                         if dct_accounting_software['bln_hr_solutions']:
# #                             temp_products += 'HR Solutions, '
# #                         if dct_accounting_software['bln_employee_management']:
# #                             temp_products += 'Employee Management, '
# #
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">Accounting Software-"""+str(count)+"""</td>
# #                         <td  valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_accounting_software['int_count'])+""" User </td>
# #                         <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Additional Features</b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td  valign="top" style="padding:5px 13px; text-align:left;">""" + temp_features.strip(', ')+"""</td>
# #                         </tr>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Other Products<b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;">""" + temp_products.strip(', ')+"""</td>
# #                         </tr>
# #                         """
# #                         # <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                     count += 1
# #                     flt_total += flt_amount
# #
# #             if ins_hr_solutions:
# #                 count = 1
# #                 for dct_hr_solutions in ins_hr_solutions:
# #                     flt_amount = dct_hr_solutions['dbl_amount']
# #                     if dct_hr_solutions['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         temp_features = ''
# #                         temp_products = ''
# #                         if dct_hr_solutions['bln_promo_campaign']:
# #                             temp_features += 'Promo Campaign, '
# #                         if dct_hr_solutions['bln_digital_marketing']:
# #                             temp_features += 'Digital Marketting, '
# #                         if dct_hr_solutions['bln_business_intelligence']:
# #                             temp_features += 'Business Intelligence, '
# #
# #                         if dct_hr_solutions['bln_enquiry_track']:
# #                             temp_products += 'Enquiry Track, '
# #                         if dct_hr_solutions['bln_accounting']:
# #                             temp_products += 'Accounting Software, '
# #                         if dct_hr_solutions['bln_employee_management']:
# #                             temp_products += 'Employee Management, '
# #
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">HR Solutions-"""+str(count)+"""</td>
# #                         <td  valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_hr_solutions['int_count'])+""" User </td>
# #                         <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Additional Features</b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td  valign="top" style="padding:5px 13px; text-align:left;">""" + temp_features.strip(', ')+"""</td>
# #                         </tr>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Other Products<b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;">""" + temp_products.strip(', ')+"""</td>
# #                         </tr>
# #                         """
# #                         # <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                     count += 1
# #                     flt_total += flt_amount
# #
# #             if ins_employee_management:
# #                 count = 1
# #                 for dct_employee_management in ins_employee_management:
# #                     flt_amount = dct_employee_management['dbl_amount']
# #                     if dct_employee_management['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         temp_features = ''
# #                         temp_products = ''
# #                         if dct_employee_management['bln_promo_campaign']:
# #                             temp_features += 'Promo Campaign, '
# #                         if dct_employee_management['bln_digital_marketing']:
# #                             temp_features += 'Digital Marketting, '
# #                         if dct_employee_management['bln_business_intelligence']:
# #                             temp_features += 'Business Intelligence, '
# #
# #                         if dct_employee_management['bln_enquiry_track']:
# #                             temp_products += 'Enquiry Track, '
# #                         if dct_employee_management['bln_accounting']:
# #                             temp_products += 'Accounting Software, '
# #                         if dct_employee_management['bln_hr_solutions']:
# #                             temp_products += 'HR Solutions, '
# #
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">Employee Management-"""+str(count)+"""</td>
# #                         <td  valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_employee_management['int_count'])+""" User </td>
# #                         <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Additional Features</b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td  valign="top" style="padding:5px 13px; text-align:left;">""" + temp_features.strip(', ')+"""</td>
# #                         </tr>
# #                         </tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;"><b>Other Products<b></td>
# #                         <tr>
# #                         <tr>
# #                             <td></td>
# #                             <td valign="top" style="padding:5px 13px; text-align:left;">""" + temp_products.strip(', ')+"""</td>
# #                         </tr>
# #                         """
# #                         # <td  valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                     count += 1
# #                     flt_total += flt_amount
# #         elif ins_user.fk_company.fk_company_type.vchr_company_type == 'MOBILE':
# #             ins_product = ItemEnquiry.objects.filter(fk_enquiry_master = ins_enquiry[0]['pk_bint_id']).values('fk_brand__vchr_brand_name',
# #             'fk_item__vchr_item_name','int_quantity','dbl_amount','vchr_enquiry_status','fk_product__vchr_product_name')
# #             if ins_product:
# #                 count = 1
# #                 for dct_product in ins_product:
# #                     flt_amount = dct_product['dbl_amount']
# #                     if dct_product['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">"""+str(dct_product['fk_product__vchr_product_name'])+""" - """+str(count)+"""</td>
# #                         <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_product['fk_brand__vchr_brand_name'])+"""
# #                          - """+str(dct_product['fk_item__vchr_item_name'])+""" - """+str(dct_product['int_quantity'])+"""No(s) </td>
# #                         <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                         """
# #                     count += 1
# #                     flt_total += flt_amount
# #
# #
# #
# #
# #
# #         #     ins_computers = ComputersEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_brand__vchr_brand_name',
# #         #   'fk_item__vchr_item_name','int_quantity','dbl_amount','vchr_enquiry_status')
# #         #     ins_tablet = TabletEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_brand__vchr_brand_name',
# #         #   'fk_item__vchr_item_name','int_quantity','dbl_amount','vchr_enquiry_status')
# #         #     ins_accessories = AccessoriesEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_brand__vchr_brand_name',
# #         #   'fk_item__vchr_item_name','int_quantity','dbl_amount','vchr_enquiry_status')
# #         #     ins_mobile = MobileEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_brand__vchr_brand_name',
# #         #   'fk_item__vchr_item_name','int_quantity','dbl_amount','vchr_enquiry_status','vchr_colour','vchr_spec')
# #           #
# #         #     # import pdb; pdb.set_trace()
# #         #     if ins_computers:
# #         #         count = 1
# #         #         for dct_computers in ins_computers:
# #         #             flt_amount = dct_computers['dbl_amount']
# #         #             if dct_computers['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #         #                 bln_send_mail = False
# #         #                 continue
# #         #             if flt_amount != 0:
# #         #                 str_html += """<tr>
# #         #                 <td valign="top" style="padding:5px 13px; color:#696a6b;">Computers - """+str(count)+"""</td>
# #         #                 <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_computers['fk_brand__vchr_brand_name'])+"""
# #         #                  - """+str(dct_computers['fk_item__vchr_item_name'])+""" - """+str(dct_computers['int_quantity'])+"""No(s) </td>
# #         #                 <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         #                 </tr>
# #         #                 """
# #         #             count += 1
# #         #             flt_total += flt_amount
# #         #     if ins_tablet:
# #         #         count = 1
# #         #         for dct_tablet in ins_tablet:
# #         #             flt_amount = dct_tablet['dbl_amount']
# #         #             if dct_tablet['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #         #                 bln_send_mail = False
# #         #                 continue
# #         #             if flt_amount != 0:
# #         #                 str_html += """<tr>
# #         #                 <td valign="top" style="padding:5px 13px; color:#696a6b;">Tablets - """+str(count)+"""</td>
# #         #                 <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_tablet['fk_brand__vchr_brand_name'])+"""
# #         #                  - """+str(dct_tablet['fk_item__vchr_item_name'])+""" - """+str(dct_tablet['int_quantity'])+"""No(s) </td>
# #         #                 <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         #                 </tr>
# #         #                 """
# #         #             count += 1
# #         #             flt_total += flt_amount
# #           #
# #         #     if ins_accessories:
# #         #         count = 1
# #         #         for dct_accessories in ins_accessories:
# #         #             flt_amount = dct_accessories['dbl_amount']
# #         #             if dct_accessories['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #         #                 bln_send_mail = False
# #         #                 continue
# #         #             if flt_amount != 0:
# #         #                 str_html += """<tr>
# #         #                 <td valign="top" style="padding:5px 13px; color:#696a6b;">Accessories - """+str(count)+"""</td>
# #         #                 <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_accessories['fk_brand__vchr_brand_name'])+"""
# #         #                  - """+str(dct_accessories['fk_item__vchr_item_name'])+""" - """+str(dct_accessories['int_quantity'])+"""No(s) </td>
# #         #                 <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         #                 </tr>
# #         #                 """
# #         #             count += 1
# #         #             flt_total += flt_amount
# #           #
# #         #     if ins_mobile:
# #         #         count = 1
# #         #         for dct_mobile in ins_mobile:
# #         #             flt_amount = dct_mobile['dbl_amount']
# #         #             if dct_mobile['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #         #                 bln_send_mail = False
# #         #                 continue
# #         #             if flt_amount != 0:
# #         #                 str_html += """<tr>
# #         #                 <td valign="top" style="padding:5px 13px; color:#696a6b;">Mobiles - """+str(count)+"""</td>
# #         #                 <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_mobile['fk_brand__vchr_brand_name'])+"""
# #         #                  - """+str(dct_mobile['fk_item__vchr_item_name'])+""" - """+str(dct_mobile['int_quantity'])+"""No(s) </td>
# #         #                 <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #         #                 </tr>
# #         #                 """
# #         #             count += 1
# #         #             flt_total += flt_amount
# #
# #         elif ins_user.fk_company.fk_company_type.vchr_company_type == 'AUTOMOBILE':
# #             ins_suv = SuvEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_model__vchr_model',
# #           'fk_variant__vchr_variant','vchr_color','dbl_amount','vchr_enquiry_status')
# #             ins_sedan = SedanEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_model__vchr_model',
# #           'fk_variant__vchr_variant','vchr_color','dbl_amount','vchr_enquiry_status')
# #             ins_hatchback = HatchbackEnquiry.objects.filter(fk_enquiry_master_id = ins_enquiry[0]['pk_bint_id']).values('fk_model__vchr_model',
# #           'fk_variant__vchr_variant','vchr_color','dbl_amount','vchr_enquiry_status',)
# #
# #             # import pdb; pdb.set_trace()
# #             if ins_suv:
# #                 count = 1
# #                 for dct_suv in ins_suv:
# #                     flt_amount = dct_suv['dbl_amount']
# #                     if dct_suv['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">Suv - """+str(count)+"""</td>
# #                         <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_suv['fk_model__vchr_model'])+"""
# #                          - """+str(dct_suv['fk_variant__vchr_variant'])+""" - """+str(dct_suv['vchr_color'])+"""</td>
# #                         <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                         """
# #                     count += 1
# #                     flt_total += flt_amount
# #
# #             if ins_sedan:
# #                 count = 1
# #                 for dct_sedan in ins_sedan:
# #                     flt_amount = dct_sedan['dbl_amount']
# #                     if dct_sedan['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">Sedan - """+str(count)+"""</td>
# #                         <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_sedan['fk_model__vchr_model'])+"""
# #                          - """+str(dct_sedan['fk_variant__vchr_variant'])+""" - """+str(dct_sedan['vchr_color'])+"""</td>
# #                         <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                         """
# #                     count += 1
# #                     flt_total += flt_amount
# #
# #             if ins_hatchback:
# #                 count = 1
# #                 for dct_hatchback in ins_hatchback:
# #                     flt_amount = dct_hatchback['dbl_amount']
# #                     if dct_hatchback['vchr_enquiry_status'] not in ['PROPOSAL SEND','BOOKED']:
# #                         bln_send_mail = False
# #                         continue
# #                     if flt_amount != 0:
# #                         str_html += """<tr>
# #                         <td valign="top" style="padding:5px 13px; color:#696a6b;">hatchback - """+str(count)+"""</td>
# #                         <td valign="top" style="padding:5px 13px; text-align:left;">"""+str(dct_hatchback['fk_model__vchr_model'])+"""
# #                          - """+str(dct_hatchback['fk_variant__vchr_variant'])+""" - """+str(dct_hatchback['vchr_color'])+"""</td>
# #                         <td valign="top" align="right" style="padding:5px 13px;">"""+ str(format(flt_amount,'.2f')) +"""</td>
# #                         </tr>
# #                         """
# #                     count += 1
# #                     flt_total += flt_amount
# #
# #         str_html +="""</table><table width="100%" border="0" cellspacing="0" cellpadding="0" background="#000" style="margin:0;"   bordercolor="#e2e2e2">
# #         <tr>
# #         <td style="padding:13px; text-align:right;">&nbsp;</td>
# #         <td style="padding:13px; text-align:right;"><strong>Total</strong></td>
# #         <td align="right" style="padding:13px;"><strong>"""+ str(format((math.ceil(flt_total*100)/100),'.2f')) +"""</strong></td>
# #         </tr>
# #         </table>
# #         </div>
# #
# #         <!--.main_warper_end-->
# #         </body>
# #         </html>
# #             """
# #
# #
# #
# #         # <div><img src="""+qrcodePath+"""></div>
# #
# #         str_footer = """ <!DOCTYPE html>
# #         <html>
# #           <head>
# #
# #           </head>
# #           <body>
# #             <div style="left:0px;    right:0px;    height:50px;    margin-bottom:0px;" >
# #             <div style=" border-bottom:1px dotted #333;"></div>
# #              <div style="width:100%; color: #696a6b; float:left; padding:10px 0; text-align:center; font-size:14px; line-height:20px; margin-right:5px;margin bottom:5px;">
# #                <p>Feel free to contact us on <strong>"""+ins_user.fk_company.vchr_email+""", """+ins_user.fk_company.vchr_phone+"""</strong></p>
# #              </div>
# #              </div>
# #           </body>
# #         </html> """
# #
# #
# #         str_header = """ <!DOCTYPE html>
# #
# #           <body><div style="width:1000px; height:100px; margin:0 auto; padding:10px; background-color:#FFF; font-family: sans-serif; float:left;">
# #           <!--.header_start-->
# #           <div style="text-align:right; padding-bottom: 15px; margin-bottom: 15px; border-bottom: 1px dotted #000;"> <img src="""+images+""" style="float:left; width:150px;height:150px;" class="img-responsive img-rounded">
# #             <h1 style="text-transform:uppercase; font-weight:300; font-size:45px; margin:5px 0; color:#1c252b;">ESTIMATION</h1>
# #             <h2 style="font-weight:bold; font-size:23px; margin:0; color:#1c252b;">"""+ins_user.fk_company.vchr_name+"""</h2>
# #             <h2 style="font-weight:100; font-size:20px; margin:0; color:#1c252b;">"""+ins_user.fk_company.vchr_address+"""</h2>
# #             <h2 style="font-weight:100; font-size:20px; margin:0; color:#1c252b;">Phone : """+ins_user.fk_company.vchr_phone+"""</h2><h2 style="font-weight:100; font-size:20px; margin:0; color:#1c252b;">Email : """+ins_user.fk_company.vchr_email+"""</h2>
# #           </div>
# #           <!--.header_end-->"""
# #         Html_file= open(settings.STATIC_DIR+'/footer.html',"w")
# #         Html_file.write(str_footer)
# #         Html_file.close()
# #
# #         fle_header= open(settings.STATIC_DIR+'/header.html',"w")
# #         fle_header.write(str_header)
# #         fle_header.close()
# #         enquiryurl = settings.HOSTNAME+"/view_enquiry/"+ins_enquiry[0]['vchr_hash']
# #         staffurl = settings.HOSTNAME+"/staff_rating/"+ins_enquiry[0]['vchr_hash']
# #
# #         # import pdb; pdb.set_trace()
# #         if flt_total != 0 and bln_send_mail:
# #             filename =settings.STATIC_DIR+'/'+ins_enquiry[0]['vchr_enquiry_num']+'.pdf'
# #             pdfkit.from_string(str_html,filename,{'--footer-html': settings.STATIC_DIR+'/footer.html','--header-html':settings.STATIC_DIR+'/header.html','header-spacing':'40','footer-left':'Page [page] of [toPage]','--footer-font-size':'8','footer-right': 'Powered by Travidux','--margin-bottom':'2cm','--footer-spacing':'40','--no-footer-line':''})
# #             to = ins_customer[0]['cust_email']
# #             to2 = ins_user.username
# #             subject =  'Enquiry Print'
# #             from_email = settings.EMAIL_HOST_EMAIL
# #             text_content = 'Travidux'
# #             html_content = '''Dear '''+str(ins_customer[0]['cust_fname']).title()+''' '''+str(ins_customer[0]['cust_lname']).title()+'''
# #             .<br> To rate the staff click <a target ='_blank' href="'''+staffurl+'''">here</a>.<br> '''
# #             # ,<br> To check out your enquiry click <a target ='_blank' href="'''+enquiryurl+'''">here</a>
# #             # import pdb; pdb.set_trace()
# #             # p = process(target=email_sent,args=(subject, text_content,from_email,to,html_content,filename))
# #             # p.start()
# #             # print("Do stuff here")
# #
# #
# #             mail = EmailMultiAlternatives(subject, text_content, from_email, [to])
# #             mail.attach_alternative(html_content, "text/html")
# #             mail.attach_file(filename)
# #             mail.send()
# #             remove(filename)
# #             return True
# #         else:
# #             return True
# #     except Exception as e:
# #         print(str(e))
# #         return True





# # @shared_task  # Use this decorator to make this a asyncronous function
# # def generate_report(data_inicial, data_final, email):
# #     generate_report_excel(
# #         ini_date = ini_date,
# #         final_date = final_date,
# #         email = email
# #     )
