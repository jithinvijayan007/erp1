from datetime import datetime
import requests

# -------------------------------------------Not completed-----------------------------------------------------

def SparePurchaseReturn():
    """
        Function to pass Purchase Return Details of Sapres to SAP by POST method.
        param:

            SAP_API_Arg :
                    Master:- MYGOAL_KEY,ShowRoomID,CardCode,CardName,DocDate,DocNum,BaseDocNum,BaseDocDate,Type
                    Details:- ItemCode,Quantity,Amount,TaxCode,Mnfserial,Costcenter,LocCode
            SAP_API_return :Success

        return: Success

    """
    try:

        rst_data = {}

        dct_master_data = {}
        dct_master_data['MYGOAL_KEY'] = ""
        dct_master_data['ShowRoomID'] = ""
        dct_master_data['CardCode'] = ""
        dct_master_data['CardName'] = ""
        dct_master_data['DocDate'] = ""
        dct_master_data['DocNum'] = ""
        dct_master_data['BaseDocNum'] = ""
        dct_master_data['BaseDocDate'] = ""
        dct_master_data['Type'] = ""
        dct_master_data['LstDetails'] = []

        dct_details_data = {}
        dct_details_data['ItemCode'] = ""
        dct_details_data['Quantity'] = ""
        dct_details_data['Amount'] = ""
        dct_details_data['TaxCode'] = ""
        dct_details_data['Mnfserial'] = ""
        dct_details_data['Costcenter'] = ""
        dct_details_data['LocCode'] = ""

        url = ""
        res_data = requests.post(url,json=dct_master_data)

        if res_data.status_code == 200: # if Succes
            ins_sap_track  = SapApiTrack.objects.create(
                                                        int_document_id = '',
                                                        int_type = 10,
                                                        int_status = 1,
                                                        dat_push = datetime.now(),
                                                        txt_remarks = 'Spare purchase return'
                                                       )
            if  ins_sap_track:
                return 1


    except Exception as e:
        raise
