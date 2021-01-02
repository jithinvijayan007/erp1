from receipt.models import Receipt
from POS import settings
from userdetails.models import UserDetails as Userdetails
from payment.models import Payment
from customer.models import CustomerDetails

import num2words

from django.core.files.storage import FileSystemStorage
import pdfkit
import base64

from tool_settings.models import Tools

def PrintPayment(int_payment_id):
        lst_html_insurance=[]

        dict_payment_details=Payment.objects.filter(pk_bint_id=int_payment_id).values("fk_branch__vchr_name","fk_branch__vchr_mygcare_no","vchr_doc_num","dat_payment","int_fop", "int_payee_type","fk_payee_id","dbl_amount","fk_bank","fk_approved_by__first_name","fk_approved_by__last_name","vchr_remarks").first()
        str_mygcare_num = dict_payment_details['fk_branch__vchr_mygcare_no'] if dict_payment_details['fk_branch__vchr_mygcare_no'] else ''
        if dict_payment_details['int_payee_type'] in [2,3]:
            dict_paid_to=Userdetails.objects.filter(user_ptr_id=dict_payment_details['fk_payee_id']).values("first_name","last_name").first()
            str_paid_to=dict_paid_to['first_name']+" "+dict_paid_to['last_name']
        else:
            str_paid_to=CustomerDetails.objects.filter(pk_bint_id=dict_payment_details['fk_payee_id']).values('vchr_name').first()['vchr_name']
        str_amount_words=num2words.num2words(dict_payment_details['dbl_amount']).title().split("Point")
        if len(str_amount_words)==2:
            str_amount_words=str_amount_words[0]+" Rupees and "+str_amount_words[1]+" Paise only/-"
        else:
            str_amount_words=str_amount_words[0] +" Rupees only/-"

        html_data="""<!doctype html>
                        <html>
                        <head>
                        <meta charset="utf-8">
                        <title>Untitled Document</title>
                	<style>
                    .imagebox{
                             width:100%;
                             float: left;
                             border-bottom: 1px solid #c7c2c2;
                             padding-bottom: 12px;margin-top: 20px;
                              }
                        .ibox1{
                        width: 25%;
                        float: left;

                              }
                        .ibox2{
                        width: 50%;
                        float: left;
                              }
                     .ibox2 h6{
                           margin-bottom: 0;
                                       margin-top: 10px;
                           padding-left: 0 !important;
                              }
                      .ibox2 p{
                           margin-bottom: 0;
                                       margin-top: 5px;
                           padding-right: 0;
                                       padding-left: 0;
                              }
                        .ibox3{
                     .imagebox{
                             width:100%;
                             float: left;
                             border-bottom: 1px solid #c7c2c2;
                             padding-bottom: 12px;margin-top: 20px;
                              }
                        .ibox1{
                        width: 25%;
                        float: left;

                              }
                        .ibox2{
                        width: 50%;
                        float: left;
                              }
                     .ibox2 h6{
                           margin-bottom: 0;
                                       margin-top: 10px;
                           padding-left: 0 !important;
                              }
                      .ibox2 p{
                           margin-bottom: 0;
                                       margin-top: 5px;
                           padding-right: 0;
                                       padding-left: 0;
                              }
                        .ibox3{
                        width: 25%;
                        float: left;
                              }    width: 25%;
                        float: left;
                              }
                	.container{
                			         width:1170px;
                			         margin:auto;

                		      }
                	    .clear{
                			        clear:both;
                			  }
                		table#voucher {
                				  border-collapse: collapse;
                				  border-spacing: 0;
                				  width: 100%;

                			  }

                	  #voucher th,#voucher td {
                				  padding: 8px;
                		     }
                	</style>

                        </head>

                        <body>
                        	<div class="container">
                                        <div class="imagebox">

                                               <div class="ibox1">
                                           <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
                                           </div>
                                           <div class="ibox2">

                                                     <div style="width:100%;float:left;">
                                    <div style="width:20%;float:left">
                                    <p><span style="font-weight: 600;">ADDRESS  : </span></p>
                                    </div>
                                    <div style="width:79%;float: right">
                                    <p> Maniyattukudi Asfa Building, Mavoor Rd, Arayidathupalam, Kozhikode, Kerala</p>
                                    </div>
                                    </div>

                                           <div style="width:50%;float:left;">

                                           <div style="width:15%;float:left">
                                           <p><span style="font-weight: 600;">PH : </span></p>
                                           </div>
                                           <div style="width:83%;float: right">
                                        <p>  0487 234566</p>
                                           </div>

                                       </div>
                                             <div style="width:50%;float:right;">

                                        <div style="width:25%;float:left">
                                           <p><span style="font-weight: 600;">MOB : </span></p>
                                           </div>
                                           <div style="width:73%;float: right">
                                        <p>   1234567890</p>
                                           </div>
                                    </div>
                                                    <div style="width:50%;float:left;">
                                       <div style="width:45%;float:left">
                                      <p><span style="font-weight: 600;">MYG CARE : </span></p>
                                       </div>
                                       <div style="width:54%;float: right">
                                    <p> """+str(str_mygcare_num)+"""</p>
                                       </div>

                                       </div>
                                             <div style="width:50%;float:right;">
                                        <div style="width:35%;float:left">
                                             <p><span style="font-weight: 600;">EMAIL ID : </span></p>
                                           </div>
                                           <div style="width:65%;float: right">
                                        <p>    contact@myg.in</p>
                                           </div>
                                    </div>
                                           <div style="width:100%;float:left;">
                                        <p><span style="font-weight: 600;">GSTN : </span>23AAAAA0000A1Z9</p>
                                       </div>

                                        </div>
                                           <div class="ibox3" style="text-align: right;">
                                           <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
                                           <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
                                           <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
                                           </div>

                        			<div style="width: 100%;float:left;text-align: center;">
                        				<h4>3G MOBILE WORLD MANIYATTUKKUDI ASFA BUILDING CALICUT-673004</h4>
                        		    </div>

                        		    <table id="voucher">
                        				    <thead>
                        						    <tr>
                        								<th colspan="3" style="text-align: center;font-size: 20px;text-decoration-line: underline;color: green;">Payment Voucher</th>
                        						    </tr>
                        				    </thead>
                        					<tbody>
                        						    <tr>
                        								<td>To,</td>
                        								<td style="text-align: right;">PV No :</td>
                        								<td style="text-align: right;width: 110px;">"""+str(dict_payment_details['vchr_doc_num'])
        html_data+="""</td>
                        						    </tr>
                        						    <tr>

                        							    <td style="padding-left: 44px;">"""+str(str_paid_to)
                                                        # Travelling Expense
        html_data+="""</td>
                        								<td style="text-align: right;">PV Date :</td>
                        								<td style="text-align: right;width: 110px;">"""+str(dict_payment_details['dat_payment'].strftime('%d-%m-%Y'))
        html_data+="""</td>
                        						    </tr>
                        						    <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;">
                        								<th colspan="2" style="text-align: left;">Particulars</th>
                        								<th style="text-align: right">Amount</th>
                        						    </tr>
                                                    <tr>
                        								 <td colspan="2">Paid by Cash Drawn at """+str(dict_payment_details['fk_branch__vchr_name'])
                                                        #  Cash Drawn at
        html_data+="""</td>
                        								 <td style="text-align: right">"""+str(dict_payment_details['dbl_amount'])+"""</td>
                        						    </tr>
                        						    <tr>
                        								<td colspan="2">"""+str(dict_payment_details['vchr_remarks'])
                        									#  Fayis Rahman.T.P (Event & Management Team)
                        									# Travelling exp from   27/8/19</span> to <span style="color: green;font-weight: 600">25/9/19

        html_data+="""<br>"""
                                            # <span style="color: green;font-weight: 600">"""+str(dict_payment_details['vchr_remarks'])+"""</span><br>
        html_data+=                									"""Rs.<span style="color: green;font-weight: 600">"""+str(dict_payment_details['dbl_amount'])+"""</span> Towards
                        								</td>
                        						    </tr>
                        					</tbody>

                        				 <tfoot>

                        					       <tr style="background-color: whitesmoke;">
                        							    <td></td>
                        							    <td style="text-align: right;font-weight: 600;">Total : </td>
                        							    <td style="text-align: right;font-weight: 600;">"""+str(dict_payment_details['dbl_amount'])
                                        # 2259.00
        html_data+="""</td>
                        					       </tr>
                        				 </tfoot>
                        		     </table>
                        		    <div class="clear"></div>
                        		    <p>"""+str_amount_words
                                    # Rupees : Two  thousand two hundred fifty nine only/-
        html_data+="""</p>
                        		    <div style="width: 25%;float:left;">
                        				 <p style="font-weight: 600;">Entered By</p>
                        		    </div>
                        		    <div style="width: 25%;float:left;">
                        				 <p style="font-weight: 600;">Verified By</p>
                        		    </div>
                        		    <div style="width: 25%;float:left;text-align: right;">
                        				 <p style="font-weight: 600;">Approved By</p>
                        		    </div>
                        		    <div style="width: 25%;float:left;text-align: right;">
                        				 <p style="font-weight: 600;">Recieved By</p>
                        		    </div>
                        	</div>
                        </body>
                        </html>"""
        try:
            pdf_path = settings.MEDIA_ROOT+'/'
            pdf_name ='PaymentVoucher.pdf'
            filename = pdf_path+pdf_name
            pdfkit.from_string(html_data,filename)
            fs = FileSystemStorage()
            lst_encoded_string=[]
            if fs.exists(filename):
                with fs.open(filename) as pdf:
                    lst_encoded_string.append(str(base64.b64encode(pdf.read())))
            file_details = {}
            file_details['file'] = lst_encoded_string
            file_details['file_name'] = pdf_name
            return file_details

        except Exception as e:
            raise


if __name__ == '__main__':
    PrintPayment(37)
