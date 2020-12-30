
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from rest_framework.response import Response
import pandas as pd
from datetime import datetime,timedelta,date


# LG
import psycopg2.extras
from django.conf import settings
try:
    userName = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    host = settings.DATABASES['default']['HOST']
    database = settings.DATABASES['default']['NAME']
    conn = psycopg2.connect(host=host,database=database, user=userName, password=password)
    # conn = psycopg2.connect(host="localhost",database="bi", user="admin", password="tms@123")
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    conn.autocommit = True
except Exception as e:
    print ("Cannot connect to Data Base..")

def get_branch():
    try:
        cur.execute("SELECT pk_bint_id,vchr_name FROM branch order by vchr_name;")
        branch = cur.fetchall()
        lst_branch = []
        for data in branch:
            dct_branch = {}
            dct_branch["name"] = data['vchr_name'].upper()
            dct_branch["id"] = data['pk_bint_id']
            lst_branch.append(dct_branch)

        return {"status":1,"branch":lst_branch}
    except Exception as e:
        return {"status":0,"data":"Oops.... Something Went Wrong!!...."}

# Create your views here.
class DetailedModelWiseSalesReport(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            data = get_branch()
            if data['status'] == 1:
                return Response({"status":1,"branch":data['branch']})
            else:
                return Response({"status":0,"data":"NO Data..."})
        except Exception as e:
            return Response({"status":0,"data":"Oops.... Something Went Wrong!!...."})

    def post(self,request):
        try:
            # {"datFrom":"2019-07-01", "datTo":"2020-07-01","lstBranch":[2,3]}
            # import pdb; pdb.set_trace()
            dat_date_from = request.data.get('datFrom', datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo', datetime.strftime(datetime.now(),'%Y-%m-%d'))
            lst_branches = request.data.get('lstBranch', [])
            str_filter = ""

            if lst_branches:
                str_filter += " AND b.pk_bint_id in ("+str(lst_branches)[1:-1]+")"
            int_cust_id=request.data.get('intCustomerId')
            int_staff_id=request.data.get('intStaffId')
            # Filters
            lst_more_filter=[]
            """CUSTOMER WISE"""
            if int_cust_id:

                str_filter += "AND sm.fk_customer_id = "+str(int_cust_id)+" "

            """STAFF WISE"""
            if int_staff_id:
                str_filter += "AND sm.fk_staff_id = "+str(int_staff_id)+" "


            if request.data.get('lstProduct'):
                str_filter +=  ' AND it.fk_product_id in ' +str(request.data.get('lstProduct')).replace('[','(').replace(']',')')
            if request.data.get("lstBrand"):
                str_filter +=  ' AND it.fk_brand_id in ' +str(request.data.get('lstBrand')).replace('[','(').replace(']',')')

            if request.data.get("lstItemCategory"):

                str_filter +=  ' AND it.fk_item_category_id in ' +str(request.data.get('lstItemCategory')).replace('[','(').replace(']',')')


            if request.data.get("lstItemGroup"):
                str_filter +=  ' AND it.fk_item_group_id in ' +str(request.data.get('lstItemGroup')).replace('[','(').replace(']',')')

            if request.data.get("lstItem"):
                str_filter +=  ' AND sd.fk_item_id in ' +str(request.data.get('lstItem')).replace('[','(').replace(']',')')

            if request.data.get("bln_smart_choice"):

                str_filter += "and it.fk_product_id !=(select pk_bint_id from products where vchr_name ilike 'smart choice') "

            if request.data.get("bln_service"):
                str_filter += "and sd.fk_master_id not in ( select sales_master.pk_bint_id from sales_master join sales_details on fk_master_id=sales_master.pk_bint_id where int_sales_status=3 and dat_invoice:: DATE BETWEEN '"+str(dat_date_from)+"' AND '"+str(dat_date_to)+"') "

            # Filters
            str_query = """SELECT
                TO_CHAR(sm.dat_created :: DATE, 'dd/mm/yyyy') as dat_invoiced,
                to_char(sm.dat_created, 'HH12:MI am') as time_invoiced,
                sd.pk_bint_id,
                b.vchr_name AS branch_name,
                sm.vchr_invoice_num AS invoice_number,
                au.first_name || ' ' || au.last_name as staff,
                pd.vchr_name AS product_name,
                brd.vchr_name AS brand_name,
                ig.vchr_item_group AS item_group,
                it.vchr_item_code AS item_code,
                it.vchr_name AS item_name,
                sd.dbl_selling_price AS sold_price,
                sd.dbl_buyback,
                ROUND((((sd.dbl_selling_price) / ('1.' || sd.dbl_tax_percentage)::NUMERIC))::NUMERIC,2) AS taxable_value,
                ROUND((sd.dbl_selling_price - (sd.dbl_selling_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC))::NUMERIC, 2) AS tax,
                jsonb_array_elements(sd.json_imei)::JSONB AS imei,
                sd.dbl_indirect_discount AS indirect_discount,
                sd.dbl_dealer_price AS dp,
                sd.dbl_cost_price AS cost_price,
                sd.dbl_mop AS mop,
                CASE WHEN sd.dbl_selling_price < 0 THEN (-1*sd.int_qty) ELSE sd.int_qty END AS qty,
                sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount AS profit_on_dp,
                CASE WHEN (sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC <=0 THEN 0 ELSE (sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC - ROUND((sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC/('1.' || sd.dbl_tax_percentage)::NUMERIC,2) END AS tax_on_profit,
                ROUND(((sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC - CASE WHEN (sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC <=0 THEN 0 ELSE (sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC - ROUND((sd.dbl_selling_price - sd.dbl_dealer_price - sd.dbl_indirect_discount)::NUMERIC/('1.' || sd.dbl_tax_percentage)::NUMERIC,2) END)::NUMERIC,2) AS net_profit_on_dp,
                ROUND((ROUND(((sd.dbl_selling_price) / ('1.' || sd.dbl_tax_percentage)::NUMERIC)::NUMERIC,2) - sd.dbl_cost_price)::NUMERIC,2) AS profit_on_costprice,
                sd.dbl_discount AS direct_discount
                FROM sales_details sd
                    JOIN sales_master sm ON sd.fk_master_id = sm.pk_bint_id
                    JOIN branch b ON b.pk_bint_id = sm.fk_branch_id
                    JOIN item it ON it.pk_bint_id = sd.fk_item_id
                    JOIN products pd ON pd.pk_bint_id = it.fk_product_id
                    JOIN brands brd ON brd.pk_bint_id = it.fk_brand_id
                    JOIN item_group ig ON ig.pk_bint_id = it.fk_item_group_id
                    JOIN auth_user au on au.id = sm.fk_staff_id
                WHERE sd.int_sales_status not in (3) and sm.dat_created::DATE BETWEEN '"""+dat_date_from+"""' and '"""+dat_date_to+"""'"""+str_filter+""" ORDER BY b.vchr_name,sm.vchr_invoice_num"""

            cur.execute(str_query)
            rst_data = cur.fetchall()
            if rst_data:
                try:
                    # import pdb; pdb.set_trace()
                    dct_report = {'Slno':[],'Branch':[],'Date':[],'Time':[], 'Invoice Number':[], 'Product':[], 'Brand':[], 'Item Group':[], 'Item Code':[], 'Item Name':[], 'Sold Price':[], 'Taxable Value':[], 'Tax':[], 'QTY':[], 'IMEI':[], 'Indirect Discount':[], 'Dealer Price':[], 'Cost Price':[], 'MOP':[], 'Profit On DP':[], 'Tax On Profit':[], 'Net Profit On DP':[], 'Profit On Cost Price':[], 'Direct Discount':[],'Staff':[],'BuyBack Amount':[]}
                    i = 1
                    # total = 0
                    for data in rst_data:

                        dct_report['Slno'].append(i)
                        # dct_report['Slno'].append(data['pk_bint_id'])
                        dct_report['Branch'].append(data['branch_name'])
                        dct_report['Date'].append(data['dat_invoiced'])
                        dct_report['Time'].append(data['time_invoiced'])
                        dct_report['Invoice Number'].append(data['invoice_number'])
                        dct_report['Staff'].append(data['staff'].title())
                        dct_report['Product'].append(data['product_name'])
                        dct_report['Brand'].append(data['brand_name'])
                        dct_report['Item Group'].append(data['item_group'])
                        dct_report['Item Code'].append(data['item_code'])
                        dct_report['Item Name'].append(data['item_name'])
                        dct_report['Sold Price'].append(data['sold_price'])
                        dct_report['Taxable Value'].append(data['taxable_value'])
                        dct_report['Tax'].append(data['tax'])
                        dct_report['QTY'].append(data['qty'])
                        dct_report['IMEI'].append(data['imei'] if data['imei'] not in  ('None','---') else '')
                        dct_report['Indirect Discount'].append(data['indirect_discount'])
                        dct_report['Dealer Price'].append(data['dp'])
                        dct_report['Cost Price'].append(data['cost_price'])
                        dct_report['MOP'].append(data['mop'])
                        dct_report['Profit On DP'].append(data['profit_on_dp'])
                        dct_report['Tax On Profit'].append(data['tax_on_profit'])
                        dct_report['Net Profit On DP'].append(data['net_profit_on_dp'])
                        dct_report['Profit On Cost Price'].append(data['profit_on_costprice'])
                        dct_report['Direct Discount'].append(data['direct_discount'])
                        dct_report['BuyBack Amount'].append(data['dbl_buyback'])
                        # total += data['sold_price']

                        i = i+1

                    # print("Model : ",total)
                    # import pdb; pdb.set_trace()
                    df = pd.DataFrame(dct_report)
                    str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_DetailedModelWiseSalesReport.xlsx'
                    filename =settings.MEDIA_ROOT+'/'+str_file


                    # if(os.path.exists(filename)):
                    #     os.remove(filename)


                    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                    workbook = writer.book
                    cell_format = workbook.add_format()
                    cell_format.set_align('center')
                    cell_format1 = workbook.add_format()
                    cell_format1.set_align('left')
                    df.to_excel(writer,index=False, sheet_name='Model Wise Sales Report',columns=['Slno','Branch','Date','Time','Invoice Number', 'Staff','Product', 'Brand', 'Item Group', 'Item Code', 'Item Name', 'Sold Price', 'Taxable Value', 'Tax', 'QTY', 'IMEI', 'Indirect Discount', 'Dealer Price', 'Cost Price', 'MOP', 'Profit On DP', 'Tax On Profit', 'Net Profit On DP', 'Profit On Cost Price', 'Direct Discount','BuyBack Amount'],startrow=6, startcol=0)
                    worksheet = writer.sheets['Model Wise Sales Report']
                    merge_format1 = workbook.add_format({
                        'bold': 20,
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_size':23
                        })

                    merge_format2 = workbook.add_format({
                    'bold': 6,
                    'border': 1,
                    'align': 'left',
                    'valign': 'vleft',
                    'font_size':13
                    })
                    worksheet.merge_range('A1+:S2', 'Detailed Model Wise Sales Report', merge_format1)
                    worksheet.merge_range('A4+:D4', 'Taken By               :  '+request.user.username, merge_format2)
                    worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)

                    # i=str(i+2)
                    # worksheet.write('F'+i, 'Total:-',cell_format)
                    # worksheet.write('G'+i, sum_soldprice_mrp,cell_format)
                    # worksheet.write('H'+i, sum_dp,cell_format)
                    # worksheet.write('I'+i, sum_servicecahrge,cell_format)
                    # worksheet.write('J'+i, sum_spareprofit,cell_format)
                    # worksheet.write('K'+i, sum_profittax,cell_format)
                    # worksheet.write('L'+i, sum_netprofitonjob,cell_format)

                    worksheet.set_column('B:B', 20,cell_format)
                    worksheet.set_column('C:C', 20,cell_format)
                    worksheet.set_column('D:D', 15,cell_format)
                    worksheet.set_column('E:E', 15,cell_format)
                    worksheet.set_column('F:F', 17,cell_format)
                    worksheet.set_column('G:G', 20,cell_format)
                    worksheet.set_column('H:H', 20,cell_format)
                    worksheet.set_column('I:I', 35,cell_format1)
                    worksheet.set_column('J:J', 16,cell_format)
                    worksheet.set_column('K:K', 75,cell_format)
                    worksheet.set_column('L:L', 15,cell_format)
                    worksheet.set_column('M:M', 15,cell_format)
                    worksheet.set_column('N:N', 15,cell_format)
                    worksheet.set_column('O:O', 15,cell_format)
                    worksheet.set_column('P:P', 25,cell_format)
                    worksheet.set_column('Q:Q', 15,cell_format)
                    worksheet.set_column('R:R', 20,cell_format)
                    worksheet.set_column('S:S', 15,cell_format)
                    worksheet.set_column('T:T', 15,cell_format)
                    worksheet.set_column('U:U', 14,cell_format)
                    worksheet.set_column('V:V', 15,cell_format)
                    worksheet.set_column('W:W', 15,cell_format)
                    worksheet.set_column('X:X', 20,cell_format)
                    worksheet.set_column('Y:Y', 15,cell_format)
                    worksheet.set_column('Z:Z', 15,cell_format)
                    # worksheet.set_column('X:X', 15,cell_format)
                    # import pdb; pdb.set_trace()
                    writer.save()
                    return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                except Exception as e:
                    # import pdb; pdb.set_trace()
                    return JsonResponse({'status':'0','message':e})
            else:
                return Response({"status":"0", "message":"No Data..."})
        except Exception as e:
            print(e)
            return Response({"status":"0", "message":"Some Thing Went wrong"})
