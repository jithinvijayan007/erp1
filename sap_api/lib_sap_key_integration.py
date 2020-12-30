from sqlalchemy import create_engine
import sys

def sap_key_integration():
    """
        Tables:
            sales_master
            receipt
            branch_stock_master
            stock_transfer
            sap_api_track
        Discription:
            Purpose of this code is to fetch sapKey from sap_api_track(Coloumn : txt_remarks) and update curresponding sapKey fields in above tables using the PK
        
            
    """
    
    try:
        # Create connection with sqlalchemy engine
        db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/myg_pos_live2"
        # db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/pos_sap"
        conn = create_engine(db_connetion_string)
    except Exception as e:
        return JsonResponse({'status':'failed','reason':'cannot connect to database'})

    try:
        str_values_sales_master = ""
        str_values_branch_stock_master = ""

        str_branch_stock_master_query = "select sat.int_document_id,sat.dat_push,sat.txt_remarks::jsonb->>'sapKey' as key from sap_api_track sat join branch_stock_master bsm on sat.int_document_id = bsm.pk_bint_id where sat.int_type in (3) and int_status in (2) and bsm.vchr_sap_doc_num is null;"
        str_stock_transfer_query = "select sat.int_document_id,sat.txt_remarks::jsonb->>'sapKey' as key from sap_api_track sat join stock_transfer st on sat.int_document_id = st.pk_bint_id where sat.int_type in (8) and sat.int_status in (2) and st.vchr_sap_doc_num is null;"
        str_sales_master_query = "select sat.int_document_id,sat.dat_push,sat.txt_remarks::jsonb->>'sapKey' as key from sap_api_track sat join sales_master sm on sat.int_document_id = sm.pk_bint_id where sat.int_type in (1) and int_status in (2) and sm.vchr_sap_key is null;"
        str_receipt_query = "select sat.int_document_id,sat.txt_remarks::jsonb->>'sapKey' as key from sap_api_track sat join receipt r on sat.int_document_id = r.pk_bint_id where sat.int_type in (4,5) and int_status in (2) and r.vchr_sap_key is null;"
        rst_sales_master_data = conn.execute(str_sales_master_query).fetchall()
        rst_receipt_data = conn.execute(str_receipt_query).fetchall()
        rst_branch_stock_master_data = conn.execute(str_branch_stock_master_query).fetchall()
        rst_stock_transfer_data = conn.execute(str_stock_transfer_query).fetchall()
        
        if rst_sales_master_data:
            for data in rst_sales_master_data:
                sapKey = data['key']
                dat_push = data['dat_push']
                pk_bint_id = data['int_document_id']
                str_values_sales_master += "("+str(pk_bint_id)+",'"+str(dat_push)+"'::TIMESTAMP,"+str(sapKey)+"),"

        if rst_branch_stock_master_data:
            for data in rst_branch_stock_master_data:
                sapKey = data['key']
                dat_push = data['dat_push']
                pk_bint_id = data['int_document_id']
                str_values_branch_stock_master += "("+str(pk_bint_id)+",'"+str(dat_push)+"'::TIMESTAMP,"+str(sapKey)+"),"


        str_update_sales_master = "update sales_master as sm set dat_sap_doc_date = lst_new.dat_push,vchr_sap_key = lst_new.key from (values "+str(str_values_sales_master)[:-1]+" ) as lst_new(pk_bint_id,dat_push,key) where lst_new.pk_bint_id = sm.pk_bint_id"
        str_update_receipt = "update receipt as r set vchr_sap_key = lst_new.key from (values"+str(rst_receipt_data)[1:-1]+") as lst_new(pk_bint_id,key) where lst_new.pk_bint_id = r.pk_bint_id"
        str_update_branch_stock_master = "update branch_stock_master as bsm set vchr_sap_doc_num = lst_new.key,dat_sap_doc_date = lst_new.date from (values "+str(str_values_branch_stock_master)[:-1]+") as lst_new(pk_bint_id,date,key) where lst_new.pk_bint_id = bsm.pk_bint_id" 
        str_update_stock_transfer = "update stock_transfer as st set vchr_sap_doc_num = lst_new.key from (values"+str(rst_stock_transfer_data)[1:-1]+") as lst_new(pk_bint_id,key) where lst_new.pk_bint_id = st.pk_bint_id"
        

        print("Sales Master : ",str_update_sales_master)
        print("Receipt : ",str_update_receipt)
        print("Branch Stock Master : ",str_update_branch_stock_master)
        print("Stock Transfer : ",str_update_stock_transfer)

        
        # conn.execute(str_update_sales_master)
        # conn.execute(str_update_receipt)
        # conn.execute(str_update_branch_stock_master)
        # conn.execute(str_update_stock_transfer)

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

sap_key_integration()
