import psycopg2
import psycopg2.extras
from datetime import datetime
import json
import requests

PASSWORD='tms@123'
DB_NAME='fahad_pos_live5'
HOST='localhost'
USERNAME='admin'
try:
    
    conn = psycopg2.connect(host=HOST,database=DB_NAME, user=USERNAME, password=PASSWORD)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    conn.autocommit=True
except Exception as e:
    print('database error '+str(e))

def branch_check(list,br_id):
    count_branch=0
    
    for i in list:
        if i['branch_id'] == br_id:
            return {'brach_count':count_branch,'rst':False}
        count_branch += 1
    # print(br_id)   
    return {'rst':True}

def item_check(list,item_id):
    # import pdb; pdb.set_trace()
    cout_item=0
    for i in list['data']:
        if i['item_code']==item_id:
            dict_result={'item':cout_item,'rst':True}
            return dict_result
        cout_item += 1
    dict_result = {'rst':False}
    return dict_result
    
def item_age_check(list,age_id):
    # import pdb; pdb.set_trace()
    cout_age=0
    for i in list['data']:
        if i['age'] == age_id:
            dict_result={"age":cout_age,'rst':True}
            return dict_result
    dict_result = {'rst':False}
    return dict_result

                
            
        

try:
    # import pdb; pdb.set_trace()
    date_today=datetime.now().date()
    # "alter table branch_stock_details add column int_bi_passed int default 0"
    cur.execute("select br.vchr_code,bd.*,bm.*,itm.vchr_item_code,itm.dbl_supplier_cost,itm.dbl_dealer_cost from branch_stock_details bd \
                 join branch_stock_master bm on bd.fk_master_id=bm.pk_bint_id join branch br on br.pk_bint_id=fk_branch_id \
                 join item itm on bd.fk_item_id =itm.pk_bint_id")
    # cur.execute('select * from branch_stock_details bd join branch_stock_master bm on bd.fk_master_id=bm.pk_bint_id where fk_branch_id = 1217')
    # cur.execute('select * from branch_stock_details bd join branch_stock_master bm on bd.fk_master_id=bm.pk_bint_id')
    ins_data=cur.fetchall()
    # import pdb; pdb.set_trace()
    dat_deliv_data=str(datetime.now())

    dict_details={} 
    lst_branch=[]
    for data in ins_data:
        branch_count=0
        item_count=0
        age_count=0

        dict_branch={} 
        dict_item={}
        dict_product={}
        dict_data={}
        
        lst_product=[]
        lst_age_data=[]
        
        int_item=data['vchr_item_code']
        int_age=(date_today - data['dat_stock'].date()).days
        
        # int_branch=data['fk_branch_id']
        int_branch=data['vchr_code']
        int_qty=data['int_qty']
        # int_br_st_dt_id=data['table_pk_id']
        flt_supp_cost=data['dbl_supplier_cost']
        flt_deal_cost=data['dbl_dealer_cost']
        # print(int_br_st_dt_id)
# age to status code --------------------------------------------------
        if int_age <= 15 :
            int_age=1
        elif int_age>=16 and int_age <= 30:
            int_age=2
        elif int_age >= 31 and int_age <= 60:
            int_age=3
        else:
            int_age=4
#end ege status -------------------------------------------------------

        dict_branch_check=branch_check(lst_branch,int_branch)   #checking branch is already in list
        if dict_branch_check['rst']:
            dict_data["age"]=int_age
            dict_data['qty']=int_qty
            # dict_data['date']=dat_deliv_data
            dict_data['spl_cost']=flt_supp_cost
            dict_data['deal_cost']=flt_deal_cost
            

            dict_item['item_code']=int_item
            lst_age_data.append(dict_data)
            dict_item['data']=lst_age_data

            dict_branch['branch_id']=int_branch
            lst_product.append(dict_item)
            dict_branch['data']=lst_product
            dict_branch['date']=dat_deliv_data

            lst_branch.append(dict_branch)
            # cur.execute("update branch_stock_details set int_bi_passed=1 where pk_bint_id='"+str(int_br_st_dt_id)+"'")
        
        else:
            branch_count=dict_branch_check['brach_count']

            dict_result=item_check(lst_branch[branch_count],int_item)
            if dict_result['rst']:
                item_count=dict_result['item']
                
                dict_age_result=item_age_check(lst_branch[branch_count]['data'][item_count],int_age)
                if dict_age_result['rst']:
                    age_count=dict_age_result['age']
                    lst_branch[branch_count]['data'][item_count]['data'][age_count]['qty']+=int_qty
                    # cur.execute("update branch_stock_details set int_bi_passed=1 where pk_bint_id='"+str(int_br_st_dt_id)+"'")
                else:
                    dict_data["age"]=int_age
                    dict_data['qty']=int_qty
                    # dict_data['date']=dat_deliv_data
                    dict_data['spl_cost']=flt_supp_cost
                    dict_data['deal_cost']=flt_deal_cost
                    lst_branch[branch_count]['data'][item_count]['data'].append(dict_data)
                    # cur.execute("update branch_stock_details set int_bi_passed=1 where pk_bint_id='"+str(int_br_st_dt_id)+"'")
            else:
                dict_data["age"]=int_age
                dict_data['qty']=int_qty
                # dict_data['date']=dat_deliv_data
                dict_data['spl_cost']=flt_supp_cost
                dict_data['deal_cost']=flt_deal_cost

                dict_item['item_code']=int_item
                lst_age_data.append(dict_data)
                dict_item['data']=lst_age_data
                dict_branch['data']=lst_product

                lst_branch[branch_count]['data'].append(dict_item)
                # cur.execute("update branch_stock_details set int_bi_passed=1 where pk_bint_id='"+str(int_br_st_dt_id)+"'")


    dict_details['items']=lst_branch
    # import pdb; pdb.set_trace()
    for i in dict_details['items']:
    # import pdb; pdb.set_trace()
        data=json.dumps(i)
        url = 'http://127.0.0.1:8000/branch/addstock_agefrom_pos/'
        headers = {"Content-type": "application/json"}
        try:
            res_data = requests.post(url,data,headers=headers)
            print(res_data)
        except Exception as e:
            print(e)

except Exception as e:
    print(e)