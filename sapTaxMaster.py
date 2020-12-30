import pandas as pd
import psycopg2
from datetime import datetime
import random
import json
def SapTaxMaster():
    try:
        try:
            conn = psycopg2.connect(host="localhost",database="pos_sap_new", user="admin", password="tms@123")
            cur = conn.cursor()
            conn.autocommit = True

        except Exception as e:
            return 'cannot connect to databse'


        lst_sap_tax_master_all = [{"Code":"IGST5","Name":"IGST @5%","Rate":5.000000},{"Code":"IGST28","Name":"IGST @28%","Rate":28.000000},{"Code":"IGST18","Name":"IGST @18%","Rate":18.000000},{"Code":"IGST12","Name":"IGST @12%","Rate":12.000000},{"Code":"IGST0","Name":"IGST @0%","Rate":0.000000},{"Code":"GST5","Name":"GST @ 5%","Rate":5.000000},{"Code":"GST28","Name":"GST @28%","Rate":28.000000},{"Code":"GST18","Name":"GST @18%","Rate":18.000000},{"Code":"GST12","Name":"GST@12%","Rate":12.000000},{"Code":"GST0","Name":"GST @0%","Rate":0.000000},{"Code":"GST5K","Name":"GST 5%+KFC 1%","Rate":6.000000},{"Code":"GST12K","Name":"GST 12%+KFC 1%","Rate":13.000000},{"Code":"GST18K","Name":"GST 18%+KFC 1%","Rate":19.000000},{"Code":"GST28K","Name":"GST 28%+KFC 1%","Rate":29.000000},{"Code":"GST0K","Name":"GST 0%+KFC 1%","Rate":1.000000},{"Code":"IGST5K","Name":"IGST 5%+KFC 1%","Rate":6.000000},{"Code":"IGST12K","Name":"IGST 12%+ KFC 1%","Rate":13.000000},{"Code":"IGST18K","Name":"IGST 18%+ KFC 1%","Rate":19.000000},{"Code":"IGST28K","Name":"IGST 28%+KFC 1%","Rate":29.000000},{"Code":"IGST0K","Name":"IGST 0%+KFC 1%","Rate":1.000000},{"Code":"GST5R","Name":"GST 5% Reverse Tax","Rate":5.000000}]


        lst_sap_tax_master_gst = [{"Code":"GST5","Name":"GST @ 5%","Rate":5.000000},{"Code":"GST28","Name":"GST @28%","Rate":28.000000},{"Code":"GST18","Name":"GST @18%","Rate":18.000000},{"Code":"GST12","Name":"GST@12%","Rate":12.000000},{"Code":"GST0","Name":"GST @0%","Rate":0.000000}]

        lst_sap_tax_master_gst_kfc = [{"Code":"GST5K","Name":"GST 5%+KFC 1%","Rate":6.000000},{"Code":"GST12K","Name":"GST 12%+KFC 1%","Rate":13.000000},{"Code":"GST18K","Name":"GST 18%+KFC 1%","Rate":19.000000},{"Code":"GST28K","Name":"GST 28%+KFC 1%","Rate":29.000000},{"Code":"GST0K","Name":"GST 0%+KFC 1%","Rate":1.000000}]

        lst_sap_tax_master_igst = [{"Code":"IGST5","Name":"IGST @5%","Rate":5.000000},{"Code":"IGST28","Name":"IGST @28%","Rate":28.000000},{"Code":"IGST18","Name":"IGST @18%","Rate":18.000000},{"Code":"IGST12","Name":"IGST @12%","Rate":12.000000},{"Code":"IGST0","Name":"IGST @0%","Rate":0.000000}]

        lst_sap_tax_master_igst_kfc = [{"Code":"IGST5K","Name":"IGST 5%+KFC 1%","Rate":6.000000},{"Code":"IGST12K","Name":"IGST 12%+ KFC 1%","Rate":13.000000},{"Code":"IGST18K","Name":"IGST 18%+ KFC 1%","Rate":19.000000},{"Code":"IGST28K","Name":"IGST 28%+KFC 1%","Rate":29.000000},{"Code":"IGST0K","Name":"IGST 0%+KFC 1%","Rate":1.000000}]

        # lst_sap_tax_master_gsr = [{"Code":"GST5R","Name":"GST 5% Reverse Tax","Rate":5.000000}]

        # import pdb; pdb.set_trace()

        cur.execute("select vchr_name,pk_bint_id from tax_master where vchr_name in ('CGST','SGST','IGST','KFC');")
        ins_ids = cur.fetchall()
        dct_ids = dict(ins_ids)

        """entry of GST"""
        for ins_tax in lst_sap_tax_master_gst:
            dct_tax_master = {}
            dct_tax_master[dct_ids['CGST']] = ins_tax['Rate']/2
            dct_tax_master[dct_ids['SGST']] = ins_tax['Rate']/2
            dct_tax_master = json.dumps(dct_tax_master)
            cur.execute("select pk_bint_id from sap_tax_master where vchr_code = '"+ins_tax['Code']+"'")
            ins_sap_tax = cur.fetchall()
            if not ins_sap_tax:
                cur.execute("INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('"+ins_tax['Code']+"','"+ins_tax['Name']+"','"+str(ins_tax['Rate'])+"','"+str(dct_tax_master)+"');")

        # import pdb; pdb.set_trace()
        """entry of GST with KFC"""
        for ins_tax in lst_sap_tax_master_gst_kfc:
            dct_tax_master = {}
            dct_tax_master[dct_ids['CGST']] = (ins_tax['Rate']-1)/2
            dct_tax_master[dct_ids['SGST']] = (ins_tax['Rate']-1)/2
            dct_tax_master[dct_ids['KFC']] = 1
            dct_tax_master = json.dumps(dct_tax_master)
            cur.execute("select pk_bint_id from sap_tax_master where vchr_code = '"+ins_tax['Code']+"'")
            ins_sap_tax = cur.fetchall()
            if not ins_sap_tax:
                cur.execute("INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('"+ins_tax['Code']+"','"+ins_tax['Name']+"','"+str(ins_tax['Rate'])+"','"+str(dct_tax_master)+"');")


        """entry of IGST"""
        for ins_tax in lst_sap_tax_master_igst:
            dct_tax_master = {}
            dct_tax_master[dct_ids['IGST']] = ins_tax['Rate']
            dct_tax_master = json.dumps(dct_tax_master)
            cur.execute("select pk_bint_id from sap_tax_master where vchr_code = '"+ins_tax['Code']+"'")
            ins_sap_tax = cur.fetchall()
            if not ins_sap_tax:
                cur.execute("INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('"+ins_tax['Code']+"','"+ins_tax['Name']+"','"+str(ins_tax['Rate'])+"','"+str(dct_tax_master)+"');")

        """entry of IGST with KFC"""
        for ins_tax in lst_sap_tax_master_igst_kfc:
            dct_tax_master = {}
            dct_tax_master[dct_ids['IGST']] = (ins_tax['Rate']-1)
            dct_tax_master[dct_ids['KFC']] = 1
            dct_tax_master = json.dumps(dct_tax_master)
            cur.execute("select pk_bint_id from sap_tax_master where vchr_code = '"+ins_tax['Code']+"'")
            ins_sap_tax = cur.fetchall()
            if not ins_sap_tax:
                cur.execute("INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('"+ins_tax['Code']+"','"+ins_tax['Name']+"','"+str(ins_tax['Rate'])+"','"+str(dct_tax_master)+"');")



        print('success')

    except Exception as e:
        import pdb; pdb.set_trace()
        raise

if __name__ == '__main__':
    SapTaxMaster()
