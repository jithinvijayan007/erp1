import psycopg2
import requests
import psycopg2.extras
import json


USERNAME = "admin"
PASSWORD = "tms@123"
DATABASE = "bi_T"
PORT = "5432"
HOST = "localhost"
MLOYAL_URL = ''
TIME_INTERVAL = 5

def mloyal_bill():
    try:
        conn = psycopg2.connect(
                                user = USERNAME,
                                password = PASSWORD,
                                database = DATABASE,
                                port = PORT,
                                host = HOST)

        cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    except Exception :
        print("CONNECTION CAN'T ESTABLISH")

    str_querry =
                """
                SELECT br.vchr_code AS store_code ,TO_CHAR(sm.dat_invoice,'YY-MM-DD') AS bill_date,
                    sm.vchr_invoice_num AS bill_no,sm.dbl_total_amt AS bill_grand_total,sm.dbl_discount AS  bill_discount ,
                    sm.dbl_total_tax AS bill_tax ,' ' AS bill_transaction_type,sm.dbl_total_amt - sm.dbl_total_tax  AS bill_gross_amount,
                    sm.dbl_total_amt AS bill_net_amount,cust_dt.vchr_name AS customer_fname, cust_dt.int_mobile AS customer_mobile,cust_dt.vchr_email  AS customer_email, ' ' AS voucher_code,
                    ' ' AS voucher_value, ' ' AS voucher_type, ' ' AS bill_tender_type, ' ' AS customer_dob, ' ' AS customer_doa,
                    TO_CHAR(NOW() ,'YYYY-MM-DD HH:mm:ss') AS bill_time,' ' AS bill_status,sm.vchr_invoice_num AS bill_transcation_no ,
                    ' ' AS  bill_discount_per, ' ' AS  bill_service_tax, ' ' AS  bill_cancel_date, ' ' AS  bill_cancel_time,
                    ' ' AS  bill_cancel_reason, ' ' AS  bill_cancel_amount, ' ' AS  bill_cancel_against, ' ' AS  bill_modify,
                    ' ' AS  bill_modify_reason, ' ' AS  bill_modify_datetime, ' ' AS  bill_remarks1, ' ' AS  bill_remarks2,
                    ' ' AS  bill_remarks3, ' ' AS  bill_remarks4, ' ' AS  bill_remarks5, ' ' AS  customer_code, ' ' AS  customer_lname,
                    ' ' AS  customer_gender, lct.vchr_district AS  customer_city, lct.vchr_name AS  customer_area, cust_dt.txt_address AS  customer_address, st.vchr_name AS  customer_state,
                    ' ' AS  customer_remarks1, ' ' AS  customer_remarks2, ' ' AS  customer_remarks3, ' ' AS  customer_remarks4, ' ' AS  customer_remarks5,
                    ' ' AS  ext_param1, ' ' AS  ext_param2, ' ' AS  ext_param3, ' ' AS  ext_param4, ' ' AS  ext_param5 ,' ' AS bill_round_off_amount,
                    ' ' AS item_serial_no, ' ' AS item_barcode,it.vchr_item_code AS item_code,it.vchr_name AS item_name,sd.dbl_amount AS item_rate,
                    dbl_selling_price AS item_net_amount ,sd.dbl_amount AS item_gross_amount,sd.int_qty AS item_quantity,
                    sd.dbl_tax_percentage AS item_discount_per,sd.dbl_discount+sd.dbl_buyback+sd.dbl_indirect_discount AS item_discount ,
                    sd.dbl_tax AS item_tax ,' ' AS item_service_tax, ' ' AS item_brand_code, ' ' AS item_brand_name, ' ' AS item_category_code,
                    ' ' AS item_category_name, ' ' AS item_group, ' ' AS item_group_name, ' ' AS item_color_code, ' ' AS item_color_name,
                    ' ' AS item_size_code, ' ' AS item_size_name, ' ' AS item_sub_category_code, ' ' AS item_sub_category_name ,
                    CASE
                        WHEN sd.int_sales_status = 0 THEN 'Return'
                        WHEN sd.int_sales_status = 1 THEN 'New'
                        WHEN  sd.int_sales_status = 2 THEN 'Return' END AS item_status ,
                    ' ' AS item_department_code, ' ' AS item_department_name, ' ' AS item_remarks1, ' ' AS item_remarks2,
                    ' ' AS item_remarks3, ' ' AS item_remarks4, ' ' AS item_remarks5
                FROM sales_master sm
                JOIN sales_details sd on sm.pk_bint_id = sd.fk_master_id
                JOIN branch br on br.pk_bint_id = sm.fk_branch_id
                JOIN item it on sd.fk_item_id  = it.pk_bint_id 
                JOIN customer_details cust_dt on (cust_dt.pk_bint_id = sm.fk_customer_id)
                JOIN states st on (st.pk_bint_id = cust_dt.fk_state_id)
                JOIN location lct on (lct.pk_bint_id = cust_dt.fk_location_id);

                """

    cursor.execute(str_querry)
    lst_bill_data = cursor.fetchall()
    dct_post_data ={}

    for dct_data in lst_bill_data:
        if dct_data['bill_no'] not in dct_post_data.keys():
            dct_post_data[dct_data['bill_no']] = {}
            dct_post_data[dct_data['bill_no']].setdefault("output", [])
            # dct_post_data[dct_data['bill_no']]["output"] = []
            dct_post_data[dct_data['bill_no']]["store_code"] = dct_data['store_code']
            dct_post_data[dct_data['bill_no']]["bill_date"] = dct_data['bill_date']
            dct_post_data[dct_data['bill_no']]["bill_no"] = dct_data['bill_no']
            dct_post_data[dct_data['bill_no']]["bill_grand_total"] = dct_data['bill_grand_total']
            dct_post_data[dct_data['bill_no']]["bill_discount"] = dct_data['bill_discount']
            dct_post_data[dct_data['bill_no']]["bill_tax"] = dct_data['bill_tax']
            dct_post_data[dct_data['bill_no']]["bill_transaction_type"] = dct_data['bill_transaction_type']
            dct_post_data[dct_data['bill_no']]["bill_gross_amount"] = dct_data['bill_gross_amount']
            dct_post_data[dct_data['bill_no']]["bill_net_amount"] = dct_data['bill_net_amount']
            dct_post_data[dct_data['bill_no']]["customer_fname"] = dct_data['customer_fname']
            dct_post_data[dct_data['bill_no']]["customer_mobile"] = dct_data['customer_mobile']
            dct_post_data[dct_data['bill_no']]["customer_email"] = dct_data['customer_email']
            dct_post_data[dct_data['bill_no']]["voucher_code"] = dct_data['voucher_code']
            dct_post_data[dct_data['bill_no']]["voucher_value"] = dct_data['voucher_value']
            dct_post_data[dct_data['bill_no']]["voucher_type"] = dct_data['voucher_type']
            dct_post_data[dct_data['bill_no']]["bill_tender_type"] = dct_data['bill_tender_type']
            dct_post_data[dct_data['bill_no']]["customer_dob"] = dct_data['customer_dob']
            dct_post_data[dct_data['bill_no']]["customer_doa"] = dct_data['customer_doa']
            dct_post_data[dct_data['bill_no']]["bill_time"] = dct_data['bill_time']
            dct_post_data[dct_data['bill_no']]["bill_type"] = dct_data['bill_type']
            dct_post_data[dct_data['bill_no']]["bill_status"] = dct_data['bill_status']
            dct_post_data[dct_data['bill_no']]["bill_transcation_no"] = dct_data['bill_transcation_no']
            dct_post_data[dct_data['bill_no']]["bill_discount_per"] = dct_data['bill_discount_per']
            dct_post_data[dct_data['bill_no']]["bill_service_tax"] = dct_data['bill_service_tax']
            dct_post_data[dct_data['bill_no']]["bill_cancel_date"] = dct_data['bill_cancel_date']
            dct_post_data[dct_data['bill_no']]["bill_cancel_time"] = dct_data['bill_cancel_time']
            dct_post_data[dct_data['bill_no']]["bill_cancel_reason"] = dct_data['bill_cancel_reason']
            dct_post_data[dct_data['bill_no']]["bill_cancel_amount"] = dct_data['bill_cancel_amount']
            dct_post_data[dct_data['bill_no']]["bill_cancel_against"] = dct_data['bill_cancel_against']
            dct_post_data[dct_data['bill_no']]["bill_modify"] = dct_data['bill_modify']
            dct_post_data[dct_data['bill_no']]["bill_modify_reason"] = dct_data['bill_modify_reason']
            dct_post_data[dct_data['bill_no']]["bill_modify_datetime"] = dct_data['bill_modify_datetime']
            dct_post_data[dct_data['bill_no']]["bill_remarks1"] = dct_data['bill_remarks1']
            dct_post_data[dct_data['bill_no']]["bill_remarks2"] = dct_data['bill_remarks2']
            dct_post_data[dct_data['bill_no']]["bill_remarks3"] = dct_data['bill_remarks3']
            dct_post_data[dct_data['bill_no']]["bill_remarks4"] = dct_data['bill_remarks4']
            dct_post_data[dct_data['bill_no']]["bill_remarks5"] = dct_data['bill_remarks5']
            dct_post_data[dct_data['bill_no']]["customer_code"] = dct_data['customer_code']
            dct_post_data[dct_data['bill_no']]["customer_lname"] = dct_data['customer_lname']
            dct_post_data[dct_data['bill_no']]["customer_gender"] = dct_data['customer_gender']
            dct_post_data[dct_data['bill_no']]["customer_city"] = dct_data['customer_city']
            dct_post_data[dct_data['bill_no']]["customer_area"] = dct_data['customer_area']
            dct_post_data[dct_data['bill_no']]["customer_address"] = dct_data['customer_address']
            dct_post_data[dct_data['bill_no']]["customer_state"] = dct_data['customer_state']
            dct_post_data[dct_data['bill_no']]["customer_remarks1"] = dct_data['customer_remarks1']
            dct_post_data[dct_data['bill_no']]["customer_remarks2"] = dct_data['customer_remarks2']
            dct_post_data[dct_data['bill_no']]["customer_remarks3"] = dct_data['customer_remarks3']
            dct_post_data[dct_data['bill_no']]["customer_remarks4"] = dct_data['customer_remarks4']
            dct_post_data[dct_data['bill_no']]["customer_remarks5"] = dct_data['customer_remarks5']
            dct_post_data[dct_data['bill_no']]["ext_param1"] = dct_data['ext_param1']
            dct_post_data[dct_data['bill_no']]["ext_param2"] = dct_data['ext_param2']
            dct_post_data[dct_data['bill_no']]["ext_param3"] = dct_data['ext_param3']
            dct_post_data[dct_data['bill_no']]["ext_param4"] = dct_data['ext_param4']
            dct_post_data[dct_data['bill_no']]["ext_param5"] = dct_data['ext_param5']
            dct_post_data[dct_data['bill_no']]["bill_round_off_amount"] = dct_data['bill_round_off_amount']
        dct_item_data = {}
        dct_item_data['item_serial_no'] = dct_data['item_serial_no']
        dct_item_data['item_barcode'] = dct_data['item_barcode']
        dct_item_data['item_code'] = dct_data['item_code']
        dct_item_data['item_name'] = dct_data['item_name']
        dct_item_data['item_rate'] = dct_data['item_rate']
        dct_item_data['item_net_amount'] = dct_data['item_net_amount']
        dct_item_data['item_gross_amount'] = dct_data['item_gross_amount']
        dct_item_data['item_quantity'] = dct_data['item_quantity']
        dct_item_data['item_discount_per'] = dct_data['item_discount_per']
        dct_item_data['item_discount'] = dct_data['item_discount']
        dct_item_data['item_tax'] = dct_data['item_tax']
        dct_item_data['item_service_tax'] = dct_data['item_service_tax']
        dct_item_data['item_brand_code'] = dct_data['item_brand_code']
        dct_item_data['item_brand_name'] = dct_data['item_brand_name']
        dct_item_data['item_category_code'] = dct_data['item_category_code']
        dct_item_data['item_category_name'] = dct_data['item_category_name']
        dct_item_data['item_group'] = dct_data['item_group']
        dct_item_data['item_group_name'] = dct_data['item_group_name']
        dct_item_data['item_color_code'] = dct_data['item_color_code']
        dct_item_data['item_color_name'] = dct_data['item_color_name']
        dct_item_data['item_size_code'] = dct_data['item_size_code']
        dct_item_data['item_size_name'] = dct_data['item_size_name']
        dct_item_data['item_sub_category_code'] = dct_data['item_sub_category_code']
        dct_item_data['item_sub_category_name'] = dct_data['item_sub_category_name']
        dct_item_data['item_status'] = dct_data['item_status']
        dct_item_data['item_department_code'] = dct_data['item_department_code']
        dct_item_data['item_department_name'] = dct_data['item_department_name']
        dct_item_data['item_remarks1'] = dct_data['item_remarks1']
        dct_item_data['item_remarks2'] = dct_data['item_remarks2']
        dct_item_data['item_remarks3'] = dct_data['item_remarks3']
        dct_item_data['item_remarks4'] = dct_data['item_remarks4']
        dct_item_data['item_remarks5'] = dct_data['item_remarks5']
        dct_post_data[dct_data['bill_no']]["output"].append(dct_item_data)

    try:

        dct_data = {}
        dct_data['objClass'] = dct_post_data.values()
        headers = {}
        if lst_bill_data:
            ecom_res = requests.post(MLOYAL_URL,json = dct_data,headers = headers)
        conn.close()
        return True
    except Exception as e:
        print(str(e))
        conn.close()


if __name__=='__main__':
    ecom_sales_status()