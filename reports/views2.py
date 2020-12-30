from invoice.models import PartialInvoice

from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from branch.models import Branch

from POS import ins_logger,settings
import sys, os

from datetime import datetime

import pandas as pd

from .views import get_col_widths
from aldjemy.core import get_engine
class CreditSaleReport(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:

            dat_from=request.data.get('datFrom')
            dat_to=request.data.get('datTo')
            dct_filter={}
            dct_filter['fk_invoice_id__isnull']=False
            dct_filter['json_updated_data__icontains']='dbl_partial_amt'


            lst_branches=[]
            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':

                pass

            else:
                dct_filter['fk_invoice__fk_branch_id']=request.user.userdetails.fk_branch_id
                lst_branches=[request.user.userdetails.fk_branch_id]

            if request.data.get('lstBranch'):
                    dct_filter['fk_invoice__fk_branch_id__in']=request.data.get('lstBranch')
                    lst_branches=request.data.get('lstBranch')
            lst_credit=PartialInvoice.objects.filter(**dct_filter,fk_invoice__dat_invoice__gte=dat_from,fk_invoice__dat_invoice__lte=dat_to,int_approve=4)\
            .annotate(dbl_invoice_amt=KeyTextTransform('dbl_partial_amt','json_updated_data'),dbl_credit_amt=KeyTextTransform('dbl_balance_amt','json_updated_data'),dbl_bill_amt=KeyTextTransform('dbl_total_amt','json_updated_data')).extra(select ={'dated':"to_char(partial_invoice.dat_invoice,'DD-MM-YYYY')"})\
            .values('fk_invoice__fk_customer__int_mobile','fk_invoice__fk_customer__vchr_name','fk_invoice__fk_branch__vchr_name','fk_invoice__vchr_invoice_num','dbl_credit_amt','dbl_bill_amt','fk_invoice_id','dated')
            str_filter_branch = ''

            if request.data.get('blnExport'):
                if lst_branches:
                      str_filter_branch=' '+", ".join(list(Branch.objects.filter(pk_bint_id__in=lst_branches).values_list('vchr_name',flat=True)))
                else:
                    str_filter_branch= 'ALL'


                sheet_name1 = 'Sheet1'

                str_dat_today=datetime.strftime(datetime.today().date(),'%d-%m-%Y')
                str_dat_from=datetime.strftime(datetime.strptime(dat_from,'%Y-%m-%d').date(),'%d-%m-%Y')
                str_dat_to=datetime.strftime(datetime.strptime(dat_to,'%Y-%m-%d').date(),'%d-%m-%Y')
                df = pd.DataFrame(list(lst_credit))

                lst_headers_order = ['DATE INVOICE','BRANCH NAME','INVOICE NUMBER','CUSTOMER MOBILE','CUSTOMER NAME','CREDIT AMOUNT','BILL AMOUNT']




                int_invoice_amt = 0
                int_credit_amt = 0
                int_bill_amt = 0



                for data in lst_credit:

                    # int_invoice_amt += data['dbl_invoice_amt']
                    int_credit_amt += int(data['dbl_credit_amt'])
                    int_bill_amt += int(data['dbl_bill_amt'])


                dct_data_selected={'CUSTOMER MOBILE':'fk_invoice__fk_customer__int_mobile','CUSTOMER NAME':'fk_invoice__fk_customer__vchr_name','BRANCH NAME':'fk_invoice__fk_branch__vchr_name','INVOICE NUMBER':'fk_invoice__vchr_invoice_num','DATE INVOICE':'dated','CREDIT AMOUNT':'dbl_credit_amt','BILL AMOUNT':'dbl_bill_amt'}
                for vchr_headers in lst_headers_order:

                    df[vchr_headers] = df[dct_data_selected.get(vchr_headers)]
                    del df[dct_data_selected.get(vchr_headers)]

                if   'fk_invoice_id'  in df.keys():
                    del df['fk_invoice_id']




                # df.loc[len(df), ['CUSTOMER NAME','DEBIT','CREDIT']]= ['', '','']




                df.loc[len(df), ['CUSTOMER MOBILE','CREDIT AMOUNT','BILL AMOUNT']]= [' ',' ',' ']

                df.loc[len(df), ['CUSTOMER MOBILE','CREDIT AMOUNT','BILL AMOUNT']]= ['TOTAL : ',int_credit_amt,int_bill_amt]


                excel_file = settings.MEDIA_ROOT+'/credit_sale_report.xlsx'
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

                df.index = pd.RangeIndex(start=1, stop=df.shape[0]+1, step=1)
                df.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=13, startcol=0)

                workbook = writer.book
                worksheet = writer.sheets[sheet_name1]

                merge_format1 = workbook.add_format({
                    'bold': 20,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size':23
                    })

                merge_format2 = workbook.add_format({
                'bold': 4,
                'border': 1,
                'align': 'left',
                'valign': 'vleft',
                'font_size':12
                })
                merge_format3 = workbook.add_format({
                'bold': 6,
                'border': 1,
                'align': 'left',
                'valign': 'vleft',
                'font_size':16
                })

                str_report = 'Credit Sale Report'
                worksheet.merge_range('A1+:D2', str_report, merge_format1)

                # worksheet.merge_range('A2+:B2',"",merge_format2)
                worksheet.merge_range('A7+:D7',"REPORT DATE         : "+str_dat_today,merge_format2)

                # worksheet.merge_range('A6+:D5',"",merge_format2)
                worksheet.merge_range('A8+:B8',"BRANCHES             : " +str_filter_branch,merge_format2)

                worksheet.merge_range('A9+:D9',"TAKEN BY               : " +request.user.userdetails.first_name.title()+' '+request.user.userdetails.last_name.title(),merge_format2)

                worksheet.merge_range('A10+:D10',"AS ON                    : "+str_dat_from+' - '+str_dat_to,merge_format2)
                # worksheet.merge_range('A8+:S7',"",merge_format2)
                # import pdb;pdb.set_trace()
                # for i,width in enumerate(get_col_widths(df)):
                #     worksheet.set_column(i-1, i-1, width)
                # worksheet.set_column(0, 0, 50)
                # worksheet.set_column(1, 1, 25)
                # #
                # worksheet.set_column(2, 2, 20)
                # worksheet.set_column(3, 3, 20)


                for i, col in enumerate(df.columns):

                    # find length of column i
                    column_len = df[col].astype(str).str.len().max()
                    # Setting the length if the column header is larger
                    # than the max column value length
                    column_len = max(column_len, len(col)) + 5
                    # set the column length
                    worksheet.set_column(i, i, column_len)

                writer.save()
                return Response({'status':1,'lst_credit':lst_credit,'export': settings.HOSTNAME+'/media/credit_sale_report.xlsx'})

            return Response({'status' : 1,'lst_credit':lst_credit})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class StockTransferHistoryExport(APIView):
    permission_classes=[AllowAny]

    def get(self,request):
        try:
            bln_branch_show = False
            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' or request.user.userdetails.fk_branch.int_type in [2,3]:
                bln_branch_show = True


            return Response({'status':1 , 'bln_branch_show' : bln_branch_show})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e) })





    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            engine = get_engine()
            connection = engine.raw_connection()
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')
            int_from_id  = request.data.get('intFromBranchId')
            int_to_id = request.data.get('intToBranchId')
            str_filter = ''
            bln_branch_option = request.data.get('blnBranchOption')
            bln_as_on = request.data.get("blnAsOn")
            dat_as_on = request.data.get("datAsOn")
            lst_transfer_status = request.data.get('transferStatus',[])
            if bln_as_on:
                str_dat_ason_exp = datetime.strftime(datetime.strptime(dat_as_on,'%Y-%M-%d'),'%d-%M-%Y')
            else:
                str_dat_from_exp = datetime.strftime(datetime.strptime(dat_from,'%Y-%M-%d'),'%d-%M-%Y')
                str_dat_to_exp = datetime.strftime(datetime.strptime(dat_to,'%Y-%M-%d'),'%d-%M-%Y')

            bln_transfer = request.data.get('blnTransfer')
            bln_received = request.data.get('blnReceived')

            str_query = """ select
                        stf.vchr_stktransfer_num as vchr_stf_num,stf.dat_created as dat_transfer,stf.dat_created as time_transfer,
                        it.vchr_item_code ,it.vchr_name as vchr_item_name, Case when ist.jsn_batch_no = '{{"batch": []}}' or ist.jsn_batch_no is null then jsn_imei->> 'imei' else jsn_batch_no->>'batch' end as imei_batch,
                        ist.int_qty as int_qty,ist.dbl_rate as dbl_amount ,stf.vchr_remarks as vchr_remark, brf.vchr_name as vchr_from_branch,brt.vchr_name as vchr_to_branch,
                        CASE When stf.int_status=1 then 'TRANSFERRED' When stf.int_status=2 then 'RECEIVED' When stf.int_status=3 then 'ACKNOWLEDGED' When stf.int_status=5 then 'PARTIALLY RECIEVED' ELSE  'BILLED' end as vchr_status ,
                        stf.vchr_eway_bill_no,TO_CHAR(tfh.dat_created,'DD-MM-YYYY') as dat_acknowledge , austf.username as vchr_tranfered_id ,autfh.username as vchr_acknowledged_id,

                        CONCAT(
                        'Packet No. :',tmd.int_packet_no,E'\n', 'CONTACT NO. :',tmd.bnt_contact_number, E'\n',\
                        'Responsible Person :',tmd.vchr_name_responsible,E'\n', 'MODE :',
                        (CASE WHEN tmd.int_medium= 1 then 'Courier' WHEN tmd.int_medium= 2 then 'BUS' WHEN tmd.int_medium= 3 then 'Direct' ELSE '' END)
                        ) as transfer_details
                        from ist_details ist

                        join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                        join auth_user austf on austf.id = stf.fk_created_id
                        join item it on ist.fk_item_id = it.pk_bint_id
                        left join transfer_history tfh  on tfh.fk_transfer_id = stf.pk_bint_id and  tfh.vchr_status ='ACKNOWLEDGED'
                        left join auth_user autfh on autfh.id = tfh.fk_created_id
                        left join  (select vchr_name_responsible,fk_transfer_id,int_medium,int_packet_no,fk_courier_id ,bnt_contact_number,dbl_expense from transfer_mode_details  group by 1,2,3,4,5,6,7) tmd on tmd.fk_transfer_id = stf.pk_bint_id
                        join branch brf on stf.fk_from_id = brf.pk_bint_id
                        join branch brt on stf.fk_to_id =brt.pk_bint_id where{0} """

            # str_filter = "stf.dat_transfer ::DATE BETWEEN '{0}' AND '{1}'".format(dat_from,dat_to )

            if bln_as_on:
                str_filter = " stf.dat_transfer ::DATE <='{0}'".format(dat_as_on)
            else:
                str_filter = " stf.dat_transfer ::DATE BETWEEN '{0}' AND '{1}'".format(dat_from,dat_to)

                # to filter by int_status of stock_transfer
            if len(lst_transfer_status) >0:
                str_filter += " AND stf.int_status in ("+str(lst_transfer_status)[1:-1]+")"

            if bln_branch_option:

                if int_from_id:
                    str_filter += ' AND stf.fk_from_id = {}'.format(int_from_id)

                if int_to_id:
                    str_filter += ' AND stf.fk_to_id = {}'.format(int_to_id)
            else:

                if bln_transfer and bln_received:
                    str_filter += ' AND ( stf.fk_from_id = {} or stf.fk_to_id = {} )'.format(request.user.userdetails.fk_branch_id,request.user.userdetails.fk_branch_id)


                elif bln_transfer:
                    str_filter += ' AND stf.fk_from_id = {}'.format(request.user.userdetails.fk_branch_id)

                elif bln_received:
                    str_filter += ' AND stf.fk_to_id = {}'.format(request.user.userdetails.fk_branch_id)

                else:
                    str_filter += ' AND ( stf.fk_from_id = {} or stf.fk_to_id = {} )'.format(request.user.userdetails.fk_branch_id,request.user.userdetails.fk_branch_id)







            str_query = str_query.format(str_filter)
            df_exp_data = pd.read_sql_query(str_query , connection)

            df_exp_data['dat_transfer'] = df_exp_data['dat_transfer'].dt.strftime('%d-%m-%Y')
            # df_exp_data['dat_acknowledge'] = df_exp_data['dat_acknowledge'].dt.strftime('%d-%m-%Y')
            df_exp_data['time_transfer'] = df_exp_data['time_transfer'].dt.strftime('%H:%M:%S')

            df_exp_data['imei_batch'] =  df_exp_data['imei_batch'].astype(str).str.strip('[],""').astype(str).str.replace('"','')

            df_exp_data.rename({
            'vchr_stf_num' : 'STN No.',
            'dat_transfer' :'DATE',
            'time_transfer' : 'Time',
            'vchr_item_code' : 'Item/Model Code',
            'vchr_item_name' : 'Item/Model Name',
            'imei_batch' : 'IMEI/BATCH NO.',
            'int_qty' : 'Qty',
            # 'dbl_amount' : 'Rate'
            'dbl_amount' : 'Amount',
            'vchr_remark' : 'Notes',
            'vchr_from_branch' : 'From Branch',
            'vchr_to_branch' : 'To Branch',
            'dat_acknowledge' : 'Acknowledged Date',
            'vchr_status' : 'Current Status',
            'vchr_eway_bill_no' : 'e - Way Bill ',
            'transfer_details' : 'Transportation Details',

            'vchr_tranfered_id' : 'Transferer Id',
            'vchr_acknowledged_id' : 'Acknowledged id'
            }, axis=1, inplace=True)



            df_exp_data.index = pd.RangeIndex(start=1, stop=df_exp_data.shape[0]+1, step=1)

            sheet_name1 = 'sheet_1'
            str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S')+'_stock_transfer.xlsx'
            filename =settings.MEDIA_ROOT+'/'+str_file
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df_exp_data.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=13, startcol=0)

            workbook = writer.book
            merge_format1 = workbook.add_format({
                'bold': 20,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':23
                })

            merge_format2 = workbook.add_format({
            'bold': 4,
            'border': 1,
            'align': 'left',
            'valign': 'vleft',
            'font_size':12
            })
            merge_format3 = workbook.add_format({
            'bold': 6,
            'border': 1,
            'align': 'left',
            'valign': 'vleft',
            'font_size':16
            })

            worksheet = writer.sheets[sheet_name1]

            str_report = 'Stock Transfer Report'
            worksheet.merge_range('A1+:S2', str_report, merge_format1)
            worksheet.merge_range('A2+:S3',"",merge_format2)
            worksheet.merge_range('A5+:D5',"REPORT DATE          : "+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'),merge_format2)
            worksheet.merge_range('A6+:D6','Taken By                 :  '+request.user.username, merge_format2)
            if bln_as_on:
                worksheet.merge_range('A7+:D7',"As On Date             : "+str_dat_ason_exp,merge_format2)
            else:
                worksheet.merge_range('A7+:D7',"REPORT PERIOD      : "+str_dat_from_exp +' to ' +str_dat_to_exp,merge_format2)




            for i, col in enumerate(df_exp_data.columns):

                # find length of column i
                column_len = df_exp_data[col].astype(str).str.len().max()
                # Setting the length if the column header is larger
                # than the max column value length
                column_len = max(column_len, len(col)) + 5
                if col in ['Notes','Transportation Details']:
                    column_len = 20

                # set the column length
                worksheet.set_column(i, i, column_len)

            writer.save()



            str_exp_path = settings.HOSTNAME+'/media/'+str_file

            return Response({'status':1,'export':str_exp_path,'str_file_name':str_file})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})
