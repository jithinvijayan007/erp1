import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import requests
import json


def stock_request_api():
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="pos", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})



        str_query="select int_document_id from sap_api_track where int_type =12 and int_status=0;"
        cur.execute(str_query)
        lst_stock_request = cur.fetchall()
        """ To push Stock request details into SAP """
        for str_id in lst_stock_request:

            dict1 = { "WHO1":{ "Req":"log1","ReqName":"log1" },"WHO2":{ "Req":"log2","ReqName":"log2" },"WHO3":{ "Req":"log3","ReqName":"log3" } }

            str_query ="select br.vchr_code as whscode, sp.vchr_code as CardCode, it.vchr_name as Dscription, pr.dat_request as ReqDate, prd.int_qty as quantity, it.vchr_item_code as ItemCode, pr.dat_created as docdate, pr.pk_bint_id as mygoal_key, lm.int_code as tolocation, pr.dat_expired as DocDueDate, pr.dat_created as DocDate, sp.vchr_code as CardCode from purchase_request pr join purchase_request_details prd on prd.fk_request_id = pr.pk_bint_id join branch br on br.pk_bint_id= pr.fk_branch_id join supplier sp on sp.pk_bint_id =pr.fk_supplier_id join item it on it.pk_bint_id= prd.fk_item_id join location_master lm  on br.fk_location_master_id=lm.pk_bint_id  where pr.pk_bint_id=" + str(str_id["int_document_id"]) + ";"
            cur.execute(str_query)
            rst_query = cur.fetchall()

            lst_LineLevel=[]
            main_dic={}
            #rst_query[0]["whscode"] = 'WHO1'
            for rst_line_level in rst_query:
                dic = {}
                dic["ItemCode"] = rst_line_level["itemcode"]
                dic['CardCode'] = rst_line_level["cardcode"]
                dic['Dscription'] = rst_line_level["dscription"]
                dic['Quantity'] = rst_line_level["quantity"]
                dic['WhsCode'] = rst_line_level["whscode"]
                lst_LineLevel.append(dic)

            dict_header=[
                    {
                        "Req" : dict1[rst_query[0]["whscode"]]["Req"],
                        "ReqName" : dict1[rst_query[0]["whscode"]]["ReqName"],
                        "MYGOAL_KEY" : rst_query[0]["mygoal_key"],
                        "BranchID" : 1 if rst_query[0]["whscode"] !='AGY' else 2,
                        "Comments" :  "Acc",
                        "DocDate" : datetime.strftime(rst_query[0]["docdate"],"%Y-%m-%d"),
                        "ShowRoomID" : rst_query[0]["whscode"],
                        "ReqDate" : datetime.strftime(rst_query[0]["reqdate"],"%Y-%m-%d"),
                        "DocDueDate" : datetime.strftime(rst_query[0]["docduedate"],"%Y-%m-%d"),
                    }
                ]
            main_dic["Header"] = dict_header
            main_dic['Line Level'] = lst_LineLevel
            str_url = "http://myglive.tmicloud.net:8084/api/In/StockRequest"
            headers = {"Content-type": "application/json"}
            data = json.dumps(main_dic)
            res_data = requests.post(str_url,data,headers=headers)
            cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.datetime.now())+"',txt_remarks='Pushed' where int_document_id ="+str(str_id["int_document_id"])+" and int_type=12")
            response = json.loads(res_data.text)
            if str(response['status']).upper() == 'SUCCESS':
                cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id["int_document_id"])+" and int_type=12")

            else:
                cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id["int_document_id"])+" and int_type=12")
        cur.close()
        conn.close()
        return
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))


if __name__=='__main__':
    stock_request_api()
