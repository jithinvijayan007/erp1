

import datetime
import psycopg2
from datetime import timedelta

def sap_api_track(start,end,dateto):
    try:
        conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
        # conn = psycopg2.connect(host="localhost",database="pos_dp", user="admin", password="tms@123")
        cur = conn.cursor()
        conn.autocommit = True
    except Exception as e:
        return 'DB Error!!'

    cur.execute("select int_type,int_document_id from sap_api_track;")
    track_data = cur.fetchall()
    # Stock Transfer
    cur.execute("SELECT pk_bint_id, dat_transfer FROM stock_transfer where (fk_to_id=(select pk_bint_id from branch where vchr_code='AGY') or fk_from_id=(select pk_bint_id from branch where vchr_code='AGY')) and dat_transfer between '"+ start +"' and '"+ end +"';")
    stock_data = cur.fetchall()
    lst_stock_transfer = []
    for data in stock_data:
        if (8,data[0]) in track_data:
            continue
        dat_date = dateto + ' ' + str(data[1].time())
        # lst_stock_transfer.append(str("("+ str(str(data[0])) +", 8, 0, '"+ str(dat_date) +"')"))
        lst_stock_transfer.append(str("("+ str(str(data[0])) +", 8, 0, '"+ str(data[1]) +"')"))

    # Receipt
    cur.execute("SELECT pk_bint_id, dat_created, dat_updated, int_fop   FROM receipt where (dat_created between '"+ start +"' and '"+ end +"' OR dat_updated between '"+ start +"' and '"+ end +"') and (int_pstatus = 0 and fk_sales_return_id is null);")
    stock_data = cur.fetchall()
    # import pdb; pdb.set_trace()
    for data in stock_data:
        if data[2] != None:
            if (5,data[0]) in track_data or (4,data[0]) in track_data:
                continue
            if data[3] in [4,5,6]:
                dat_date = dateto + ' ' + str(data[2].time())
                # lst_stock_transfer.append(str("("+ str(data[0]) +", 5, 0, '"+ str(dat_date) +"')"))
                lst_stock_transfer.append(str("("+ str(data[0]) +", 5, 0, '"+ str(data[2]) +"')"))
            else:
                dat_date = dateto + ' ' + str(data[1].time())
                # lst_stock_transfer.append(str("("+ str(data[0]) +", 4, 0, '"+ str(dat_date) +"')"))
                lst_stock_transfer.append(str("("+ str(data[0]) +", 4, 0, '"+ str(data[2]) +"')"))
        else:
            if (5,data[0]) in track_data or (4,data[0]) in track_data:
                continue
            if data[3] in [4,5,6]:
                dat_date = dateto + ' ' + str(data[2].time())
                # lst_stock_transfer.append(str("("+ str(data[0]) +", 5, 0, '"+ str(dat_date) +"')"))
                lst_stock_transfer.append(str("("+ str(data[0]) +", 5, 0, '"+ str(data[1]) +"')"))
            else:
                dat_date = dateto + ' ' + str(data[1].time())
                # lst_stock_transfer.append(str("("+ str(data[0]) +", 4, 0, '"+ str(dat_date) +"')"))
                lst_stock_transfer.append(str("("+ str(data[0]) +", 4, 0, '"+ str(data[1]) +"')"))

    # Sales Return
    # import pdb; pdb.set_trace()
    # cur.execute("SELECT pk_bint_id, dat_created, dbl_indirect_discount  FROM sales_return where dat_created  between '"+ start +"' and '"+ end +"';")
    cur.execute("select sm.pk_bint_id,sm.dat_created,sr.dbl_indirect_discount from sales_return sr join sales_master sm on sm.pk_bint_id = sr.fk_sales_id WHERE sm.dat_created::date  between '"+ start +"' and '"+ end +"';")
    stock_data = cur.fetchall()
    lst_double_check = []
    for data in stock_data:
        if (6,data[0]) not in track_data and '(6-'+str(data[0])+')' not in lst_double_check:
            lst_double_check.append('(6-'+str(data[0])+')')
            dat_date = dateto + ' ' + str(data[1].time())
            lst_stock_transfer.append(str("("+ str(data[0]) +", 6, 0, '"+ str(data[1]) +"')"))

        if (16,data[0]) not in track_data and '(16-'+str(data[0])+')' not in lst_double_check:
            lst_double_check.append('(16-'+str(data[0])+')')
            dat_date = dateto + ' ' + str(data[1].time())
            if data[2] != 0.0:
                lst_stock_transfer.append(str("("+ str(data[0]) +", 16, 0, '"+ str(data[1]) +"')"))


    # Branch Stock Master
    cur.execute("SELECT distinct (bsd.fk_master_id) as o, bsm.pk_bint_id, bsm.dat_stock from branch_stock_details bsd join branch_stock_master  bsm on bsd.fk_master_id = bsm.pk_bint_id where (bsm.dat_stock between  '"+ start +"' and '"+ end +"') and (bsd.fk_transfer_details_id is not null);")
    stock_data = cur.fetchall()
    for data in stock_data:
        if (3,data[0]) in track_data:
            continue
        dat_date = dateto + ' ' + str(data[2].time())
        # lst_stock_transfer.append(str("("+ str(data[1]) +", 3, 0, '"+ str(dat_date) +"')"))
        lst_stock_transfer.append(str("("+ str(data[1]) +", 3, 0, '"+ str(data[2]) +"')"))

    # Payment
    # import pdb; pdb.set_trace()
    cur.execute("SELECT pk_bint_id, dat_created  FROM payment where dat_created  between '"+ start +"' and '"+ end +"';")
    stock_data = cur.fetchall()
    for data in stock_data:
        if (7,data[0]) in track_data:
            continue
        dat_date = dateto + ' ' + str(data[1].time())
        # lst_stock_transfer.append(str("("+ str(data[0]) +", 7, 0, '"+ str(dat_date) +"')"))
        lst_stock_transfer.append(str("("+ str(data[0]) +", 7, 0, '"+ str(data[1]) +"')"))

    # Inserting to database
    # import pdb; pdb.set_trace()
    cur.execute("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values "+','.join(lst_stock_transfer)+";")

dat_today= datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
dat_next = datetime.datetime.strftime(datetime.datetime.now()+timedelta(days=1),'%Y-%m-%d')

dat_today='2020-07-06'
dat_next='2020-07-06'  #datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
sap_api_track(dat_today,dat_next,'2020-06-25')
