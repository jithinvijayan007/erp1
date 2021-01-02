from branch_stock.models import BranchStockImeiDetails
from purchase.models import GrnDetails
from internal_stock.models import StockTransferImeiDetails
from invoice.models import SalesDetails
from userdetails.models import UserPermissions,UserDetails as Userdetails
from django.db.models import Q
from branch.models import Branch
import json

def check_if_imei_exist(vchr_imei,bln_transit=False,bln_sales=False,dct_filter_bs={},dct_filter_grn={},dct_filter_st={},dct_filter_sales={}):
        bln_branch_stock=BranchStockImeiDetails.objects.filter((Q(jsn_imei__imei__icontains='"'+vchr_imei+'"') or Q(jsn_imei__imei__icontains="'"+vchr_imei+"'")),**dct_filter_bs).exists()
        bln_grn_details=GrnDetails.objects.filter((Q(jsn_imei_avail__imei_avail__icontains='"'+vchr_imei+'"') or Q(jsn_imei_avail__imei__icontains="'"+vchr_imei+"'")),**dct_filter_grn).exists()
        bln_transfered = False
        dct_filter_st['fk_details__fk_transfer__int_status__in']=[1,2]
        if bln_transit:
            bln_transfered=StockTransferImeiDetails.objects.filter((Q(jsn_imei__imei__icontains='"'+vchr_imei+'"') or Q(jsn_imei__imei__icontains="'"+vchr_imei+"'")),**dct_filter_st).exists()
        bln_sold = False
        if bln_sales:
            bln_sold=SalesDetails.objects.filter((Q(json_imei__icontains='"'+vchr_imei+'"') or Q(json_imei__icontains="'"+vchr_imei+"'")),int_sales_status=1,**dct_filter_sales).exists()
        return bln_branch_stock or bln_grn_details or bln_transfered or bln_sold


def get_user_privileges(request):
    dct_data = {}
    if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN', 'BRANCH MANAGER', 'ASSISTANT BRANCH MANAGER', 'ASM1', 'ASM2', 'ASM3', 'ASM4']:
        return dct_data
    ins_user_permission = UserPermissions.objects.filter(fk_user_id = request.user.id, bln_active=True).values().last()
    if ins_user_permission:

        if ins_user_permission["jsn_branch_type"]:
            ins_branches = list(Branch.objects.filter(int_type__in = ins_user_permission["jsn_branch_type"],int_status = 0).values_list("pk_bint_id",flat=True))
            dct_data['lst_branches'] = ins_branches
        else:
            dct_data['lst_branches'] = ins_user_permission['jsn_branch'] if ins_user_permission['jsn_branch'] else []
        dct_data['lst_products'] = ins_user_permission['jsn_product'] if ins_user_permission['jsn_product'] else []
        dct_data['lst_item_groups'] = ins_user_permission['jsn_item_group'] if ins_user_permission['jsn_item_group'] else []
    return dct_data
def get_price_perm(id):
    dct_data ={'bln_mrp':False, 'bln_mop':False, 'bln_dp':False, 'bln_cost_price':False}
    if Userdetails.objects.filter(user_ptr_id = id).values('fk_group__vchr_name').first()['fk_group__vchr_name'] in  ['ADMIN']:

        dct_data ={'bln_mrp':True, 'bln_mop':True, 'bln_dp':True, 'bln_cost_price':True}
        return dct_data
    ins_user_permission = UserPermissions.objects.filter(fk_user_id = id, bln_active=True).values('json_price_perm').last()
    if ins_user_permission:
        if ins_user_permission['json_price_perm']:
            dct_perm  = json.loads(ins_user_permission['json_price_perm'])
            dct_data['bln_mrp'] = dct_perm['bln_mrp'] if dct_perm else False
            dct_data['bln_mop'] = dct_perm['bln_mop'] if dct_perm else False
            dct_data['bln_dp'] = dct_perm['bln_dp'] if dct_perm else False
            dct_data['bln_cost_price'] = dct_perm['bln_cost_price'] if dct_perm else False


    return dct_data
