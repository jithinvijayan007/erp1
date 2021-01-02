from customer.models import CustomerDetails,SalesCustomerDetails
from invoice.models import PartialInvoice,SalesMasterJio,SalesMaster
from datetime import datetime
from userdetails.models import UserDetails as Userdetails
from django.db import transaction

def SalesCustomer():
    """ Function to create sales_customer corresponds to customer and update fk_customer in sales_master,sales_master_jio,partial_invoice tables

        Steps:
        1)
            alter table sales_master add column fk_sales_customer_id BIGINT REFERENCES sales_customer_details(pk_bint_id);
            alter table sales_master_jio add column fk_sales_customer_id BIGINT REFERENCES sales_customer_details(pk_bint_id);

        2)  Uncomment fk_customer,fk_sales_customer in SalesMaster and SalesMasterJio model before run this script.and after comment it.

        3)
            alter table sales_master drop column fk_customer_id ;
            alter table sales_master_jio  drop column fk_customer_id ;
            alter table sales_master RENAME fk_sales_customer_id to fk_customer_id;
            alter table sales_master_jio  RENAME fk_sales_customer_id to fk_customer_id;

        4) select setval('sales_customer_details_pk_bint_id_seq',(select pk_bint_id from sales_customer_details order by 1 desc limit 1),true);
    """
    try:
        with transaction.atomic():
            lst_updated = []
            lst_sales_customer = []
            lst_exist = []
            lst_customer = CustomerDetails.objects.values()

            int_user = Userdetails.objects.filter(fk_group_id__vchr_name = 'ADMIN').values('user_ptr_id').first()['user_ptr_id']
            for customer in lst_customer:
                if SalesCustomerDetails.objects.filter(fk_customer_id = customer['pk_bint_id'],fk_created_id = int_user):
                    lst_exist.append(SalesCustomerDetails.objects.filter(fk_customer_id = customer['pk_bint_id'],fk_created_id = int_user).values('pk_bint_id').first()['pk_bint_id'])
                    continue
                else:
                    ins_sales_customer = SalesCustomerDetails(
                                                                dat_created = datetime.now(),
                                                                dbl_purchase_amount = customer['dbl_purchase_amount'],
                                                                fk_created_id = int_user,
                                                                fk_customer_id = customer['pk_bint_id'],
                                                                fk_location_id = customer['fk_location_id'],
                                                                fk_loyalty_id = customer['fk_loyalty_id'],
                                                                fk_state_id = customer['fk_state_id'],
                                                                int_loyalty_points = customer['int_loyalty_points'],
                                                                int_mobile = customer['int_mobile'],
                                                                int_otp_number = customer['int_otp_number'],
                                                                int_redeem_point = customer['int_redeem_point'],
                                                                pk_bint_id = customer['pk_bint_id'],
                                                                txt_address = customer['txt_address'],
                                                                vchr_code = customer['vchr_code'],
                                                                vchr_email = customer['vchr_email'],
                                                                vchr_gst_no = customer['vchr_gst_no'],
                                                                vchr_loyalty_card_number = customer['vchr_loyalty_card_number'],
                                                                vchr_name = customer['vchr_name']
                                                            )
                    ins_sales_customer.save()
                    lst_sales_customer.append(ins_sales_customer.pk_bint_id)

                    lst_sales_master = SalesMaster.objects.filter(fk_customer_id = customer['pk_bint_id']).update(fk_sales_customer_id = ins_sales_customer.pk_bint_id)
                    lst_sales_master_jio = SalesMasterJio.objects.filter(fk_customer_id = customer['pk_bint_id']).update(fk_sales_customer_id = ins_sales_customer.pk_bint_id)

                    lst_par_inv = PartialInvoice.objects.filter(json_data__int_cust_id = customer['pk_bint_id']).values('pk_bint_id','json_data')
                    for item in lst_par_inv:
                        dct_json_data = {}
                        dct_json_data = item['json_data']
                        dct_json_data['int_sales_cust_id'] = ins_sales_customer.pk_bint_id
                        ins_update = PartialInvoice.objects.filter(pk_bint_id = item['pk_bint_id']).update(json_data = dct_json_data)
                        if ins_update:
                            lst_updated.append(item['pk_bint_id'])


            print('lst_updated -> ',lst_updated)
            print('lst_sales_customer -> ',lst_sales_customer)
            print('lst_exist-> ',lst_exist)
            return 1
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    cust = SalesCustomer()
    if cust:
        print('All Added Successfully')
