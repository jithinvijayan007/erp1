import psycopg2.extras
try:
    connpos = psycopg2.connect(host="localhost",database="pos", user="admin", password="tms@123")
    curpos = connpos.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    connpos.autocommit = True

    connbi = psycopg2.connect(host="localhost",database="bi", user="admin", password="tms@123")
    curbi = connbi.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    connbi.autocommit = True
except Exception as e:
    print ("Cannot connect to Data Base..")

def get_data_bi():

    lst_data = []

    str_query = "select distinct ie.fk_enquiry_master_id,it.vchr_item_code,ie.dbl_dealer_price,ie.dbl_cost_price,ie.dbl_mrp_price,ie.dbl_mop_price from item_enquiry ie join items it on it.id = ie.fk_item_id where ie.vchr_enquiry_status in ('INVOICED','RETURNED','IMAGE PENDING') and ie.dbl_dealer_price is not null and ie.vchr_enquiry_status not in ('LOST')order by 1 desc"
    # import pdb; pdb.set_trace()  and ie.fk_enquiry_master_id = 31384 
    curbi.execute(str_query)
    rst_data = curbi.fetchall()
    if rst_data:
        for data in rst_data:
            dct_temp = {}
            dct_temp['em_id'] = data['fk_enquiry_master_id']
            dct_temp['item_code'] = data['vchr_item_code']
            dct_temp['dp'] = data['dbl_dealer_price']
            dct_temp['cost_price'] = data['dbl_cost_price']
            dct_temp['mrp'] = data['dbl_mrp_price']
            dct_temp['mop'] = data['dbl_mop_price']
            lst_data.append(dct_temp)
        # print(lst_data)
        put_pos_data(lst_data)

def put_pos_data(lst_data):

    str_value = ""
    if lst_data:
        for data in lst_data:
            """bulck update values"""
            # str_value += "("+str(data['em_id'])+",'"+str(data['item_code'])+"',"+str(data['dp'])+","+str(data['cost_price'])+","+str(data['mrp'])+","+str(data['mop'])+"),"

            """update one by one"""
            dct_item_id = {}
            query_item_id = "select pk_bint_id,vchr_item_code from item"
            curpos.execute(query_item_id)
            rst_data = curpos.fetchall()
            if rst_data:
                for item in rst_data:
                    dct_item_id[item['vchr_item_code']] = item['pk_bint_id']
            # import pdb; pdb.set_trace()
            str_query_fk_invoice = "select fk_invoice_id from partial_invoice where int_enq_master_id = "+str(data['em_id'])+" and fk_invoice_id is not null"
            curpos.execute(str_query_fk_invoice)
            rst_data1 = curpos.fetchall()
            if rst_data:
                # import pdb; pdb.set_trace()
                for invoice_id in rst_data1:
                    print("enquiry master id : ",data['em_id'])
                    print("invoice_id : ",invoice_id['fk_invoice_id'])
                    print("Item Id : ",dct_item_id[data['item_code']])
                    str_query = "UPDATE sales_details as sd set dbl_dealer_price = "+str(data['dp'])+", dbl_cost_price = "+str(data['cost_price'])+", dbl_mrp = "+str(data['mrp'])+", dbl_mop = "+str(data['mop'])+", dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC where sd.fk_master_id = "+str(invoice_id['fk_invoice_id'])+" and sd.fk_item_id = "+str(dct_item_id[data['item_code']])+" returning sd.pk_bint_id"

                    curpos.execute(str_query)
                    updated = curpos.fetchall()
                    if curpos:
                        print("Success...")
                        print("Updated : ",len(updated))

        """updating int_sales_status = 1"""
        """updating items that is not updated in the above query"""

        str_query_for_not_updated_items = """
            select 
                DISTINCT
                sd.fk_item_id,
                sd.dbl_dealer_price,
                sd.dbl_cost_price,
                sd.dbl_mrp,
                sd.dbl_mop
                from(
                select 
                    fk_item_id,
                    count(*)
                    from 
                    (select
                        DISTINCT
                        sd.fk_item_id,
                        sd.dbl_dealer_price,
                        sd.dbl_cost_price,
                        sd.dbl_mrp,
                        sd.dbl_mop
                        from sales_details sd 
                            join item it on it.pk_bint_id = sd.fk_item_id 
                            join products pd on pd.pk_bint_id = it.fk_product_id 
                        where dbl_dealer_price is not null 
                            and int_sales_status = 1 
                            and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE')
                            and sd.fk_item_id in (select sd.fk_item_id 
                                                    from sales_details sd 
                                                        join item it on it.pk_bint_id = sd.fk_item_id 
                                                        join products pd on pd.pk_bint_id = it.fk_product_id 
                                                    where dbl_dealer_price is null 
                                                        and int_sales_status in (1) 
                                                        and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE'))
                        group by sd.dbl_dealer_price,sd.dbl_cost_price,sd.dbl_mrp,sd.dbl_mop,sd.fk_item_id) as val
                    group by fk_item_id) as val1 
                    join sales_details sd on sd.fk_item_id = val1.fk_item_id
                where val1.count = 1 and sd.dbl_dealer_price is not null;
        """
        curpos.execute(str_query_for_not_updated_items)
        rst_not_updated = curpos.fetchall()
        if rst_not_updated:
            for data in rst_not_updated:
                str_query = "update sales_details sd set dbl_dealer_price = "+str(data['dbl_dealer_price'])+", dbl_cost_price = "+str(data['dbl_cost_price'])+", dbl_mrp = "+str(data['dbl_mrp'])+", dbl_mop = "+str(data['dbl_mop'])+", dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC where sd.dbl_dealer_price is null and sd.fk_item_id = "+str(data['fk_item_id'])+" returning sd.pk_bint_id"
                # print(str_query)

                curpos.execute(str_query)
                updated = curpos.fetchall()
                if curpos:
                    print("Success...")
                    print("Updated : ",len(updated))

        """Updating items with different dp,mop,mrp,costprice"""

        str_query_for_not_updated_items1 = """
            select 
                DISTINCT
                sd.fk_item_id,
                sd.dbl_dealer_price,
                sd.dbl_cost_price,
                sd.dbl_mrp,
                sd.dbl_mop,
                max(dat_created::date) as max_date,
                min(dat_created::date) as min_date
                from(
                select 
                    fk_item_id,
                    count(*)
                    from 
                    (select
                        DISTINCT
                        sd.fk_item_id,
                        sd.dbl_dealer_price,
                        sd.dbl_cost_price,
                        sd.dbl_mrp,
                        sd.dbl_mop
                        from sales_details sd 
                            join item it on it.pk_bint_id = sd.fk_item_id 
                            join products pd on pd.pk_bint_id = it.fk_product_id 
                        where dbl_dealer_price is not null 
                            and int_sales_status = 1 
                            and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE')
                            and sd.fk_item_id in (select sd.fk_item_id 
                                                    from sales_details sd 
                                                        join item it on it.pk_bint_id = sd.fk_item_id 
                                                        join products pd on pd.pk_bint_id = it.fk_product_id 
                                                    where dbl_dealer_price is null 
                                                        and int_sales_status in (1) 
                                                        and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE'))
                        group by sd.dbl_dealer_price,sd.dbl_cost_price,sd.dbl_mrp,sd.dbl_mop,sd.fk_item_id) as val
                    group by fk_item_id) as val1 
                    join sales_details sd on sd.fk_item_id = val1.fk_item_id
                    join sales_master sm on sm.pk_bint_id = sd.fk_master_id
                where val1.count > 1 and sd.dbl_dealer_price is not null
                group by sd.fk_item_id,sd.dbl_dealer_price,sd.dbl_cost_price,sd.dbl_mrp,sd.dbl_mop order by 1,7,6;
        """
        curpos.execute(str_query_for_not_updated_items1)
        rst_not_updated1 = curpos.fetchall()
        if rst_not_updated1:
            for data in rst_not_updated1:
                str_query = "update sales_details sd set dbl_dealer_price = "+str(data['dbl_dealer_price'])+", dbl_cost_price = "+str(data['dbl_cost_price'])+", dbl_mrp = "+str(data['dbl_mrp'])+", dbl_mop = "+str(data['dbl_mop'])+", dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC from sales_master sm where sm.pk_bint_id = sd.fk_master_id and sd.dbl_dealer_price is null and sd.fk_item_id = "+str(data['fk_item_id'])+" and sd.dbl_dealer_price is null and sm.dat_created::date between '"+str(data['min_date'])+"' and '"+str(data['max_date'])+"' returning sd.pk_bint_id"
                # print(str_query)
                curpos.execute(str_query)
                updated = curpos.fetchall()
                if curpos:
                    print("Success...")
                    print("Updated : ",len(updated))

        """"updating item that is not updated in abode cases"""
        print("Updating all items whith sd.int_sales_status = 1 and sd.dealer_price is null")
        str_query = """UPDATE sales_details as sd
            SET 
            dbl_dealer_price = it.dbl_dealer_cost,
            dbl_cost_price = it.dbl_supplier_cost,
            dbl_mrp = it.dbl_mrp,
            dbl_mop = it.dbl_mop,
            dbl_tax_percentage = CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END
            FROM item as it,products as pd where it.pk_bint_id = sd.fk_item_id and pd.pk_bint_id = it.fk_product_id and sd.dbl_dealer_price is null and sd.int_sales_status in (1) and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE') returning sd.pk_bint_id"""
        curpos.execute(str_query)
        updated = curpos.fetchall()
        if curpos:

            print("Success...")
            print("Updated : ",len(updated))


        """Udating values for int_sales_status 0"""
        """updating items that is not updated in the above query"""

        str_query_for_not_updated_items = """
            select 
                DISTINCT
                sd.fk_item_id,
                sd.dbl_dealer_price,
                sd.dbl_cost_price,
                sd.dbl_mrp,
                sd.dbl_mop
                from(
                select 
                    fk_item_id,
                    count(*)
                    from 
                    (select
                        DISTINCT
                        sd.fk_item_id,
                        sd.dbl_dealer_price,
                        sd.dbl_cost_price,
                        sd.dbl_mrp,
                        sd.dbl_mop
                        from sales_details sd 
                            join item it on it.pk_bint_id = sd.fk_item_id 
                            join products pd on pd.pk_bint_id = it.fk_product_id 
                        where dbl_dealer_price is not null 
                            and int_sales_status = 1 
                            and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE')
                            and sd.fk_item_id in (select sd.fk_item_id 
                                                    from sales_details sd 
                                                        join item it on it.pk_bint_id = sd.fk_item_id 
                                                        join products pd on pd.pk_bint_id = it.fk_product_id 
                                                    where dbl_dealer_price is null 
                                                        and int_sales_status in (0) 
                                                        and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE'))
                        group by sd.dbl_dealer_price,sd.dbl_cost_price,sd.dbl_mrp,sd.dbl_mop,sd.fk_item_id) as val
                    group by fk_item_id) as val1 
                    join sales_details sd on sd.fk_item_id = val1.fk_item_id
                where val1.count = 1 and sd.dbl_dealer_price is not null;
        """
        curpos.execute(str_query_for_not_updated_items)
        rst_not_updated = curpos.fetchall()
        if rst_not_updated:
            for data in rst_not_updated:
                str_query = "update sales_details sd set dbl_dealer_price = "+str(data['dbl_dealer_price']*-1)+", dbl_cost_price = "+str(data['dbl_cost_price']*-1)+", dbl_mrp = "+str(data['dbl_mrp']*-1)+", dbl_mop = "+str(data['dbl_mop']*-1)+", dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC where sd.dbl_dealer_price is null and sd.fk_item_id = "+str(data['fk_item_id'])+" returning sd.pk_bint_id"
                # print(str_query)

                curpos.execute(str_query)
                updated = curpos.fetchall()
                if curpos:
                    print("Success...")
                    print("Updated : ",len(updated))

        """Updating items with different dp,mop,mrp,costprice"""

        str_query_for_not_updated_items1 = """
            select 
                DISTINCT
                sd.fk_item_id,
                sd.dbl_dealer_price,
                sd.dbl_cost_price,
                sd.dbl_mrp,
                sd.dbl_mop,
                max(dat_created::date) as max_date,
                min(dat_created::date) as min_date
                from(
                select 
                    fk_item_id,
                    count(*)
                    from 
                    (select
                        DISTINCT
                        sd.fk_item_id,
                        sd.dbl_dealer_price,
                        sd.dbl_cost_price,
                        sd.dbl_mrp,
                        sd.dbl_mop
                        from sales_details sd 
                            join item it on it.pk_bint_id = sd.fk_item_id 
                            join products pd on pd.pk_bint_id = it.fk_product_id 
                        where dbl_dealer_price is not null 
                            and int_sales_status = 1 
                            and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE')
                            and sd.fk_item_id in (select sd.fk_item_id 
                                                    from sales_details sd 
                                                        join item it on it.pk_bint_id = sd.fk_item_id 
                                                        join products pd on pd.pk_bint_id = it.fk_product_id 
                                                    where dbl_dealer_price is null 
                                                        and int_sales_status in (0) 
                                                        and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE'))
                        group by sd.dbl_dealer_price,sd.dbl_cost_price,sd.dbl_mrp,sd.dbl_mop,sd.fk_item_id) as val
                    group by fk_item_id) as val1 
                    join sales_details sd on sd.fk_item_id = val1.fk_item_id
                    join sales_master sm on sm.pk_bint_id = sd.fk_master_id
                where val1.count > 1 and sd.dbl_dealer_price is not null
                group by sd.fk_item_id,sd.dbl_dealer_price,sd.dbl_cost_price,sd.dbl_mrp,sd.dbl_mop order by 1,7,6;
        """
        curpos.execute(str_query_for_not_updated_items1)
        rst_not_updated1 = curpos.fetchall()
        if rst_not_updated1:
            for data in rst_not_updated1:
                str_query = "update sales_details sd set dbl_dealer_price = "+str(data['dbl_dealer_price']*-1)+", dbl_cost_price = "+str(data['dbl_cost_price']*-1)+", dbl_mrp = "+str(data['dbl_mrp'])+", dbl_mop = "+str(data['dbl_mop']*-1)+", dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC from sales_master sm where sm.pk_bint_id = sd.fk_master_id and sd.dbl_dealer_price is null and sd.fk_item_id = "+str(data['fk_item_id'])+" and sd.dbl_dealer_price is null and sm.dat_created::date between '"+str(data['min_date'])+"' and '"+str(data['max_date'])+"' returning sd.pk_bint_id"
                # print(str_query)
                curpos.execute(str_query)
                updated = curpos.fetchall()
                if curpos:
                    print("Success...")
                    print("Updated : ",len(updated))

        """"updating item that is not updated in abode cases"""
        print("Updating all items whith sd.int_sales_status = 1 and sd.dealer_price is null")
        str_query = """UPDATE sales_details as sd
            SET 
            dbl_dealer_price = it.dbl_dealer_cost::NUMERIC*-1,
            dbl_cost_price = it.dbl_supplier_cost::NUMERIC*-1,
            dbl_mrp = it.dbl_mrp::NUMERIC*-1,
            dbl_mop = it.dbl_mop::NUMERIC*-1,
            dbl_tax_percentage = CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END
            FROM item as it,products as pd where it.pk_bint_id = sd.fk_item_id and pd.pk_bint_id = it.fk_product_id and sd.dbl_dealer_price is null and sd.int_sales_status in (0) and pd.vchr_name not in ('SMART CHOICE','SERVICE','SPARE') returning sd.pk_bint_id"""
        curpos.execute(str_query)
        updated = curpos.fetchall()
        if curpos:

            print("Success...")
            print("Updated : ",len(updated))


            # str_query = "UPDATE sales_details as sd set dbl_dealer_price = "+str(data['dp'])+", dbl_cost_price = "+str(data['cost_price'])+", dbl_mrp = "+str(data['mrp'])+", dbl_mop = "+str(data['mop'])+", dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC where sd.fk_master_id in (select fk_invoice_id from partial_invoice where int_enq_master_id = "+str(data['em_id'])+" and fk_invoice_id is not null) and sd.fk_item_id = (select pk_bint_id from item where vchr_item_code = '"+str(data['item_code'])+"')returning sd.pk_bint_id"

            # curpos.execute(str_query)
            # updated = curpos.fetchall()
            # if curpos:
            #     print("Success...")
            #     print("Updated : ",len(updated))
                # if len(updated) == 0:
                #     import pdb; pdb.set_trace()


        """this is the qurey for bulck update"""
        # if str_value:
        #     print("Update Started....")
        #     str_query = """UPDATE sales_details as sd set dbl_dealer_price = lst_new.dbl_dealer_price, dbl_cost_price = lst_new.dbl_cost_price, dbl_mrp = lst_new.dbl_mrp, dbl_mop = lst_new.dbl_mop, dbl_tax_percentage = (CASE WHEN (sd.json_tax::jsonb->>'dblIGST%') is not null and (sd.json_tax::jsonb->>'dblIGST%')::numeric != 0 THEN (sd.json_tax::jsonb->>'dblIGST%')::numeric WHEN (sd.json_tax::jsonb->>'dblSGST%') is not null AND (sd.json_tax::jsonb->>'dblCGST%') is not null AND (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblSGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblCGST%')::numeric !=0 AND (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC !=0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) WHEN (sd.json_tax::jsonb->>'dblKFC%') is not null and (sd.json_tax::jsonb->>'dblKFC%')::numeric != 0 THEN ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric + (sd.json_tax::jsonb->>'dblKFC%')::NUMERIC) ELSE ((sd.json_tax::jsonb->>'dblSGST%')::numeric + (sd.json_tax::jsonb->>'dblCGST%')::numeric) END)::NUMERIC from (values """+str_value[:-1]+""") as lst_new(id,item_code,dbl_dealer_price,dbl_cost_price,dbl_mrp,dbl_mop) where sd.fk_master_id in (select fk_invoice_id from partial_invoice where int_enq_master_id = lst_new.id and fk_invoice_id is not null) and sd.fk_item_id = (select pk_bint_id from item where vchr_item_code = lst_new.item_code) returning sd.pk_bint_id"""
        #     # print(str_query)
        #     curpos.execute(str_query)
        #     updated = curpos.fetchall()
        #     if curpos:
        #         print("Success...")
        #         print("Updated : ",len(updated))
            


get_data_bi()
# put_pos_data("hello")

# db alter query
    # ALTER TABLE sales_details 
    # ADD COLUMN dbl_dealer_price DOUBLE PRECISION, 
    # ADD COLUMN dbl_cost_price DOUBLE PRECISION, 
    # ADD COLUMN dbl_mrp DOUBLE PRECISION, 
    # ADD COLUMN dbl_mop DOUBLE PRECISION, 
    # ADD COLUMN dbl_tax_percentage DOUBLE PRECISION;

# ALTER TABLE sales_details ADD COLUMN dbl_dealer_price DOUBLE PRECISION, ADD COLUMN dbl_cost_price DOUBLE PRECISION, ADD COLUMN dbl_mrp DOUBLE PRECISION, ADD COLUMN dbl_mop DOUBLE PRECISION, ADD COLUMN dbl_tax_percentage DOUBLE PRECISION;
