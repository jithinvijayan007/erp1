from math import floor,log10,pow
from branch.models import Branch
from group_level.models import GroupLevel
from userdetails.models import UserDetails as AuthUser
# from hierarchy.models import Hierarchy
from collections import OrderedDict
# from assign_branch.models import AssignBranch

import json
import requests
from django.core.mail import EmailMultiAlternatives
from os import remove
import time

def convert_to_millions(flt_number):
    """
    to convert amount to small string like(1000 = 1k)
    float amount parameter
    return a string values
    """
    flt_abs_number = 0

    if flt_number != 0:
        flt_abs_number = abs(flt_number)

    else:
        return 0.0


    lst_suffix = ['','K','M','B']
    str_number= str(round(flt_abs_number / pow(1000,floor(log10(flt_abs_number)/3)),2)) + lst_suffix[floor(log10(flt_abs_number)/3)]

    if flt_number < 0:
        return "-"+str_number
    else:
        return str_number

# def show_data_based_on_role(str_group,int_area_id):
#     """ """
#     if not str_group:
#         return "Not a valid group."
#     if not int_area_id:
#         return "Not a valid area id"

#     str_group = str_group.upper()
#     rst_branch = []
#     import pdb; pdb.set_trace()
#     # if str_group in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
#     #     rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
#     # elif LevelHierarchy.objects.filter(json_group__contains={'groups':[str_group]},bln_active=True,vchr_filter__in = ['ALL','COUNTRY','STATE']):
#     #     rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
#     if str_group == 'TERRITORY MANAGER':
#         rst_branch = Branch.objects.filter(fk_territory_id = int_area_id).values_list('pk_bint_id',flat='True')
#     elif str_group =='ZONE MANAGER':
#         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id = int_area_id).values_list('pk_bint_id',flat='True')
#     elif str_group in ['STATE HEAD','MARKETING','SERVICE HEAD']:
#         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id = int_area_id).values_list('pk_bint_id',flat='True')
#     elif str_group in ['COUNTRY HEAD','MODERN TRADE HEAD','PURCHASE MANAGER','GENERAL MANAGER SALES']:
#         rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat='True')
#     elif str_group in ['FINANCE SALES ADMIN','FINANCE MANAGER','INTERNAL AUDITOR']:
#         rst_branch = Branch.objects.values_list('pk_bint_id',flat='True')
#     return list(rst_branch)

def show_data_based_on_role(str_group,int_area_id):
    """ """
    if not str_group:
        return "Not a valid group."
    if not int_area_id:
        return "Not a valid area id"

    str_group = str_group.upper()
    rst_branch = []
    if str_group == 'TERRITORY MANAGER':
        rst_branch = Branch.objects.filter(fk_territory_id = int_area_id).values_list('pk_bint_id',flat='True')
    elif str_group =='ZONE MANAGER':
        rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id = int_area_id).values_list('pk_bint_id',flat='True')
    elif str_group in ['STATE HEAD','MARKETING','SERVICE HEAD']:
        rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id = int_area_id).values_list('pk_bint_id',flat='True')
    elif str_group in ['COUNTRY HEAD','MODERN TRADE HEAD','PURCHASE MANAGER','GENERAL MANAGER SALES']:
        rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat='True')
    elif str_group in ['FINANCE SALES ADMIN','FINANCE MANAGER','INTERNAL AUDITOR']:
        rst_branch = Branch.objects.values_list('pk_bint_id',flat='True')
    return list(rst_branch)


def show_data_based_on_hierarchy(user):
    rst_branch = get_branch_on_permission(user)
    # if user.is_superuser or LevelHierarchy.objects.filter(json_group__contains={'groups':[user.usermodel.fk_group_id]},bln_active=True,vchr_filter='ALL'):
    #     rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
    # else:
    #     ins_hierarchy = 0
    #     if user.usermodel.fk_department_id:
    #         ins_hierarchy = LevelHierarchy.objects.filter(json_group__contains={'groups':[user.usermodel.fk_group_id]},bln_active=True,fk_department_id=user.usermodel.fk_department_id).values('vchr_filter').last()
    #     else:
    #         ins_hierarchy = LevelHierarchy.objects.filter(json_group__contains={'groups':[user.usermodel.fk_group_id]},bln_active=True).values('vchr_filter').last()
    #     if ins_hierarchy['vchr_filter'].upper() == 'BRANCH':
    #         rst_branch = Branch.objects.filter(pk_bint_id=user.usermodel.fk_branch_id).values_list('pk_bint_id',flat=True)
    #     elif ins_hierarchy['vchr_filter'].upper() == 'TERRITORY':
    #         rst_branch = Branch.objects.filter(fk_territory_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
    #     elif ins_hierarchy['vchr_filter'].upper() == 'ZONE':
    #         rst_branch = Branch.objects.filter(fk_territory__fk_zone_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
    #     elif ins_hierarchy['vchr_filter'].upper() in ['STATE','SERVICE HEAD']:
    #         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
    #     elif ins_hierarchy['vchr_filter'].upper() == 'COUNTRY':
    #         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id__fk_country_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
    #     elif ins_hierarchy['vchr_filter'].upper() == 'USER':
    #         rst_branch = []

    return list(rst_branch)

# LG 21-07-2020
def get_branch_on_permission(user):
    """Permission wise filter for Branch"""
    rst_branch = []
    flag = 0
    # import pdb; pdb.set_trace()
    if user.usermodel.fk_department.vchr_code.upper()=='HOD':
        rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
    elif user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
        rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
    elif user.is_superuser or LevelHierarchy.objects.filter(json_group__contains={'groups':[user.usermodel.fk_group_id]},bln_active=True,vchr_filter__in = ['ALL','COUNTRY','STATE']):
        rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
    else:
        ins_hierarchy = 0
        if user.usermodel.fk_department_id:
            ins_hierarchy = LevelHierarchy.objects.filter(json_group__contains={'groups':[user.usermodel.fk_group_id]},bln_active=True,fk_department_id=user.usermodel.fk_department_id).values('vchr_filter').last()
        else:
            ins_hierarchy = LevelHierarchy.objects.filter(json_group__contains={'groups':[user.usermodel.fk_group_id]},bln_active=True).values('vchr_filter').last()
        if ins_hierarchy['vchr_filter'].upper() == 'TERRITORY' and user.usermodel.int_area_id:
            rst_branch = Branch.objects.filter(fk_territory_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
        elif ins_hierarchy['vchr_filter'].upper() == 'ZONE' and user.usermodel.int_area_id:
            rst_branch = Branch.objects.filter(fk_territory__fk_zone_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
        elif ins_hierarchy['vchr_filter'].upper() in ['SERVICE HEAD'] and user.usermodel.int_area_id:
            rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
        elif ins_hierarchy['vchr_filter'].upper() == 'COUNTRY' and user.usermodel.int_area_id:
            rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id__fk_country_id=user.usermodel.int_area_id).values_list('pk_bint_id',flat=True)
        elif user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','SERVICE ENGINEER','SERVICE MANAGER']:
            rst_branch.append(user.usermodel.fk_branch_id)
        elif user.usermodel.fk_group.vchr_name.upper()=='AM SERVICE':
            rst_branch= AssignBranch.objects.filter(fk_user_id=user.id).values('json_branch').first()['json_branch']['branch_id']
            rst_branch = [int(i) for i in rst_branch]
        elif user.usermodel.int_area_id:
            str_group = user.usermodel.fk_group.vchr_name.upper()
            int_area_id = user.usermodel.int_area_id
            if str_group == 'TERRITORY MANAGER':
                rst_branch = Branch.objects.filter(fk_territory_id = int_area_id).values_list('pk_bint_id',flat='True')
            elif str_group =='ZONE MANAGER':
                rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id = int_area_id).values_list('pk_bint_id',flat='True')
            elif str_group in ['STATE HEAD','MARKETING','SERVICE HEAD']:
                rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id = int_area_id).values_list('pk_bint_id',flat='True')
            elif str_group in ['COUNTRY HEAD','MODERN TRADE HEAD','PURCHASE MANAGER','GENERAL MANAGER SALES']:
                rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
            elif str_group in ['FINANCE SALES ADMIN','FINANCE MANAGER','INTERNAL AUDITOR']:
                rst_branch = Branch.objects.filter().values_list('pk_bint_id',flat=True)
            elif ins_hierarchy['vchr_filter'].upper() in ['STAFF','BRANCH']:
                rst_branch = Branch.objects.filter(pk_bint_id=user.usermodel.fk_branch_id).values_list('pk_bint_id',flat=True)
            elif ins_hierarchy['vchr_filter'].upper() == 'USER':
                rst_branch = []

    return list(rst_branch)


def notifications_data(lst_notifications):
    dct_data={}
    url='https://mygoal.biz:2021/livealert'
    dct_data['username']=[data['username'] for data in lst_notifications]
    dct_data['str_enquiry_id']=lst_notifications[0]['str_enquiry_id']
    dct_data['url']=lst_notifications[0]['url']
    dct_data['msg']=lst_notifications[0]['msg']
    dct_data['str_notification_type']=lst_notifications[0]['str_notification_type']
    dct_data['int_notification_id'] = [data['int_notification_id'] for data in lst_notifications]

    # if str_notification_type == 'ENQUIRY':json_data=json.dumps(dct_data)
    # payload_data=json.loads(json_data)

    #     dct_data['str_enquiry_id']=str_enquiry_id
    try:
        json_data=json.dumps(dct_data)
        payload_data=json.loads(json_data)
        requests.get(url, data=payload_data)
    except Exception as msg:
        print('failed to find node server')
        pass
        # return JsonResponse({'status':'failed','data':str(msg)})
# def email_sent(subject, text_content, from_email,to,html_content,filename):
#     # time.sleep(100)
#     mail = EmailMultiAlternatives(subject, text_content, from_email, [to])
#     mail.attach_alternative(html_content, "text/html")
#     mail.attach_file(filename)
#     mail.send()
#     remove(filename)
#     print("threading")

def chart_data_sort(request,dct_data,str_sort,int_page,str_report=None):
    try:
        if str_sort.upper() =='NORMAL': #Normal ordering only for creating chart

            dct_data_temp = dct_data[int_page]
            lst_keys = list(dct_data_temp.keys())
            sorted_dct_data = []
            # create normal dictionary
            if len(lst_keys) >= 10:
                start = 0
                end = 10
            else:
                start = 0
                end = len(lst_keys)
            for int_index in lst_keys[start:end]:
                rst_data = {}
                rst_data[int_index] = dct_data_temp[int_index]
                sorted_dct_data.append(rst_data)
            return sorted_dct_data
        # elif str_sort.upper() =='ASCENDING':#ascending ordering
        else:#
            dct_temp = {}
            # get all data from paginated dictionry
            for int_index in dct_data:
                dct_temp.update(dct_data[int_index])
            if str_report:
                if str_sort.upper() =='GOOD':#ascending ordering
                    # order all keys in ascending in demand item report
                    lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Sale'],-dct_temp[i]['diff']),reverse =True)
                else:
                    # order all keys in ascending in demand item report
                    lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Sale'],-dct_temp[i]['diff']),reverse =False)
            else: #ascending or descending order
                if str_sort.upper() =='GOOD':#ascending ordering
                    if request.data['type'].upper() == 'SALE':
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Sale']),reverse =True)
                    else:
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Enquiry']),reverse =True)
                else:#descend ordering
                    if request.data['type'].upper() == 'SALE':
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Sale']),reverse =False)
                    else:
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Enquiry']),reverse =False)
            sorted_dct_data = []
            # create ordered dictionary
            if len(lst_sort_key) >= (int_page*10):
                start = (int_page-1)*10
                end = int_page*10
            else:
                start = (int_page-1)*10
                end = len(lst_sort_key)
            for int_index in lst_sort_key[start:end]:
                rst_data = {}
                rst_data[int_index] = dct_temp[int_index]
                sorted_dct_data.append(rst_data)
            return sorted_dct_data

    except Exception as e:
        print('sorting failed')
        pass

def general_chart_data_sort(request,dct_data,str_sort,int_page,str_report=None):
    try:
        # import pdb; pdb.set_trace()
        if str_sort.upper() =='NORMAL':#Normal ordering only for creating chart
            dct_data_temp = dct_data[int_page]
            lst_keys = list(dct_data_temp.keys())
            sorted_dct_data = []
            # create normal dictionary
            if len(lst_keys) >= 10:
                start = 0
                end = 10
            else:
                start = 0
                end = len(lst_keys)
            # for int_index in lst_sort_key[start:end]:
            for int_index in lst_keys[start:end]:
                rst_data = {}
                rst_data[int_index] = dct_data_temp[int_index]
                sorted_dct_data.append(rst_data)
            return sorted_dct_data
        # elif str_sort.upper() =='ASCENDING':#descend ordering
        else: #ascending or descending order
            dct_temp = {}
            # get all data from paginated dictionry
            for int_index in dct_data:
                dct_temp.update(dct_data[int_index])

            if str_report:# order all keys in descending in demand item report
                if str_sort.upper() == 'GOOD':#ascend ordering
                    lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value2'],-dct_temp[i]['diff']),reverse =True)
                else:#ascend ordering
                    lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value2'],-dct_temp[i]['diff']),reverse =False)
            else:
                if str_sort.upper() == 'GOOD':#ascend ordering
                    if request.data['report_type'].upper() == 'SALE':
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value2']),reverse =True)
                    else:
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value1']),reverse =True)
                else:#descend ordering
                    if request.data['report_type'].upper() == 'SALE':
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value2']),reverse =False)
                    else:
                        lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value1']),reverse =False)
                    # lst_sort_key = sorted(dct_temp, key = lambda i: (dct_temp[i]['Value2']),reverse =False)
            sorted_dct_data = []
            # create ordered dictionary
            if len(lst_sort_key) >= (int_page*10):
                start = (int_page-1)*10
                end = int_page*10
            else:
                start = (int_page-1)*10
                end = len(lst_sort_key)
            for int_index in lst_sort_key[start:end]:
                rst_data = {}
                rst_data[int_index] = dct_temp[int_index]
                sorted_dct_data.append(rst_data)
            return sorted_dct_data

    except Exception as e:
        print('sorting failed')
        pass


# def level_data(int_group):
#     """ """
#     if not int_group:
#         return "Not a valid group."
#
#     ins_glevel=GroupLevel.objects.filter(fk_group_id=int_group).values('int_level','vchr_filter')
#     str_filter=ins_glevel.first().vchr_filter
#     if filter== 'TERRITORY':
#         rst_branch=rst_branch=Branch.objects.filter(fk_territory_id = 19).values_list('pk_bint_id',flat='True')
#         rst_user = AuthUser.objects.filter(fk_branch_id__in =rst_branch).values('pk_bint_id')
#         rst_groups=GroupLevel.objects.filter(int_level__lt=ins_glevel[0]['int_level']).values_list('fk_group__vchr_name',flat=True)
#         rst_user=user_app
#         lst_user=AuthUser.objects.fk_branch_id
#     str_group = str_group.upper()
#     if str_group == 'TERRITORY MANAGER':
#         rst_branch = Branch.objects.filter(fk_territory_id = int_area_id).values_list('pk_bint_id',flat='True')
#     elif str_group == 'ZONE MANAGER':
#         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id = int_area_id).values_list('pk_bint_id',flat='True')
#     elif str_group in ['STATE HEAD','MARKETING']:
#         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id = int_area_id).values_list('pk_bint_id',flat='True')
#     elif str_group == 'COUNTRY HEAD':
#         rst_branch = Branch.objects.filter(fk_territory_id__fk_zone_id__fk_state_id__fk_country_id = int_area_id).values_list('pk_bint_id',flat='True')
#
#     return list(rst_branch)


#for selecting product ids respect to the list of user
def get_user_products(lst_user_id):
    try:
        # import pdb; pdb.set_trace()
        lst_product_id=[]
        rst_product_id = list(AuthUser.objects.filter(user_ptr_id__in = lst_user_id).values('json_product_id'))
        for ins_product in rst_product_id:
            if ins_product['json_product_id']:
                lst_product_id.extend(ins_product['json_product_id']['productId'])
        lst_product_id = list(map(int, lst_product_id))
        lst_product_id = list(OrderedDict.fromkeys(lst_product_id))
        return lst_product_id
    except Exception as e:
        print(str(e))
        pass
