# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated,AllowAny
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from leave_management.models import Leave, LeaveType, SetLeave
# from django.db.models import Q
# from POS import ins_logger
# import traceback
# import sys, os
# from aldjemy.core import get_engine
# from hierarchy.models import HierarchyLevel
# from hierarchy.views import get_data, get_hierarchy
# from os import path
# from django.conf import settings
# import pandas as pd
# import calendar
# from user_model.models import UserDetails
# from django.db.models.functions import Concat
# from django.db.models import CharField, Value as V
# # from datetime import datetime
# from datetime import datetime, date, timedelta
# engine = get_engine()
# class AddLeaveType(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             """Add Leave Type"""
#             ins_dup_leave_type = LeaveType.objects.filter(vchr_name = request.data.get("strLeaveName"),int_year=request.data.get("intYear"),bln_active = True)
#             if ins_dup_leave_type:
#                 return Response({'status':0,'reason':'Leave Type Already Exists'})

#             ins_leave_type = LeaveType.objects.create(vchr_name = request.data.get("strLeaveName"),
#                                                             dbl_leaves_per_month = request.data.get("intMaxLeavePMonth"),
#                                                             dbl_leaves_per_year = request.data.get("intLeavePYear"),
#                                                             int_year = request.data.get("intYear"),
#                                                             vchr_remarks = request.data.get("strRemarks"),
#                                                             fk_company_id = request.user.userdetails.fk_company_id or None,
#                                                             bln_active = True)

#             return Response({'status':1})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

#     def get(self,request):
#         try:
#             # import pdb; pdb.set_trace()
#             """View Leave Type"""
#             if request.GET.get("id"):
#                 lst_leave_type =list(LeaveType.objects.filter(pk_bint_id = int(request.GET.get("id"))).values('vchr_name',
#                                                                                                               'dbl_leaves_per_month',
#                                                                                                               'dbl_leaves_per_year',
#                                                                                                               'vchr_remarks',
#                                                                                                               'int_year'))

#             else:
#                 """List Leave Type"""
#                 lst_leave_type =list(LeaveType.objects.filter(bln_active = True).values('vchr_name',
#                                                                                         'dbl_leaves_per_month',
#                                                                                         'dbl_leaves_per_year',
#                                                                                         'int_year','pk_bint_id'))
#             return Response({'status':1,'lst_leave_type':lst_leave_type})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


#     def put(self,request):
#         try:
#             """Update Leave Type"""
#             # import pdb; pdb.set_trace()
#             int_leavetype_id = request.data.get("intId")
#             str_name = request.data.get("strLeaveName")
#             ins_dup_leave_type = LeaveType.objects.filter(vchr_name = str_name,int_year=request.data.get("intYear"),bln_active = True).exclude(pk_bint_id = int_leavetype_id)

#             if ins_dup_leave_type:
#                 return Response({'status':0,'reason':'Leave Type Already Exists'})

#             ins_leave_type = LeaveType.objects.filter(pk_bint_id = int_leavetype_id).update(vchr_name = str_name,
#                                                                                             dbl_leaves_per_month = request.data.get("intMaxLeavePMonth"),
#                                                                                             dbl_leaves_per_year = request.data.get("intLeavePYear"),
#                                                                                             vchr_remarks = request.data.get("strRemarks"),
#                                                                                             int_year =  request.data.get("intYear"))

#             return Response({'status':1})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

#     def patch(self,request):
#         try:
#             """Delete Leave Type"""

#             int_leavetype_id = request.data.get("intId")
#             LeaveType.objects.filter(pk_bint_id = int_leavetype_id).update(bln_active = False)
#             return Response({'status':1})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})



# class LeaveList(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         try:
#             lst_leave_types = list(LeaveType.objects.filter(bln_active=True,int_year=datetime.now().year).values('vchr_name','pk_bint_id'))
#             return Response({'status':1,'lst_leavetypes':lst_leave_types})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':'error'})

#     def post(self,request):
#         try:
#             conn = engine.connect()
#             dat_from = datetime.strptime(request.data.get('datLeaveFrom') , '%Y-%m-%d')
#             dat_to = datetime.strptime(request.data.get('datLeaveTo') , '%Y-%m-%d')
#             int_type = request.data.get('intLeaveTypeId')
#             int_status = request.data.get('intType')
#             str_leave_type =  request.data.get('strLeaveType')
#             lst_desig = []
#             lst_leave = []

#             str_filter = ""
#             str_filter_dty = ""
#             str_filter_wkoff = ""
#             """Leave type filter"""
#             if int_type and str_leave_type not in ['ONDUTY', 'WEEKOFF']:
#                 str_filter = " AND lt.pk_bint_id = "+str(int_type)+" "

#             """Leave status filter"""
#             if int_status:
#                 str_filter += " AND le.int_status = "+str(int_status)+" "
#                 if int_status==1:
#                     str_filter_dty += " AND od.int_status = 0 "
#                     str_filter_wkoff += " AND wklv.int_status in (1, 2) "
#                 elif int_status==2:
#                     str_filter_dty += " AND od.int_status in (1,2) "
#                     str_filter_wkoff += " AND wklv.int_status = 3 "
#                 elif int_status==3:
#                     str_filter_dty += " AND od.int_status = -1 "
#                     str_filter_wkoff += " AND wklv.int_status = -1 "

#             """Branch filter"""
#             if request.data.get('intBranchId'):
#                 int_branch_id = request.data.get('intBranchId')
#                 str_filter += "AND ud.fk_branch_id ="+str(int_branch_id)+" "
#                 str_filter_dty += "AND ud.fk_branch_id ="+str(int_branch_id)+" "
#                 str_filter_wkoff += "AND ud.fk_branch_id ="+str(int_branch_id)+" "
#             else:
#                 lst_loc = request.user.userdetails.json_physical_loc
#                 if request.user.userdetails.vchr_employee_code!= 'MYGE-611' and request.user.userdetails.fk_desig.vchr_name not in ['GM SPECIAL PROJECTS','BUISNESS HEAD','MANAGER - BUSINESS OPERATIONS'] and request.user.userdetails.fk_department.vchr_name != 'HR & ADMIN':
#                     str_filter += "AND ud.json_physical_loc ?| ARRAY"+str(lst_loc)+" "
#                     str_filter_dty += "AND ud.json_physical_loc ?| ARRAY"+str(lst_loc)+" "
#                     str_filter_wkoff += "AND ud.json_physical_loc ?| ARRAY"+str(lst_loc)+" "


#             """Department filter"""
#             if request.data.get('intDepartmentId'):
#                 int_department_id = request.data.get('intDepartmentId')
#                 str_filter += " AND dept.pk_bint_id = "+str(int_department_id)+" "
#                 str_filter_dty += " AND dept.pk_bint_id = "+str(int_department_id)+" "
#                 str_filter_wkoff += " AND dept.pk_bint_id = "+str(int_department_id)+" "
#                 if request.data.get('intDesigId'):
#                     int_desig_id=request.data.get('intDesigId')
#                     str_filter += " AND desg.pk_bint_id = "+str(int_desig_id)+" "
#                     str_filter_dty += " AND desg.pk_bint_id = "+str(int_desig_id)+" "
#                     str_filter_wkoff += " AND desg.pk_bint_id = "+str(int_desig_id)+" "
#             else:
#                 if request.data.get('intDesigId'):
#                     int_desig_id=request.data.get('intDesigId')
#                     str_filter += " AND desg.pk_bint_id = "+str(int_desig_id)+" "
#                     str_filter_dty += " AND desg.pk_bint_id = "+str(int_desig_id)+" "
#                     str_filter_wkoff += " AND desg.pk_bint_id = "+str(int_desig_id)+" "
#                 else:
#                     int_desig_id = request.user.userdetails.fk_desig_id
#                     int_department_id = request.user.userdetails.fk_department_id
#                     if request.user.userdetails.fk_desig.vchr_name == 'GM SPECIAL PROJECTS' or request.user.userdetails.fk_desig.vchr_name == 'BUISNESS HEAD':
#                         ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_reporting_to=int_desig_id).values('fk_designation_id')
#                         for item in ins_hierarchy:
#                             lst_desig.append(item['fk_designation_id'])
#                         if not lst_desig:
#                             return Response({'status':'failed'})
#                         str_filter += "  AND desg.pk_bint_id IN("+str(lst_desig)[1:-1]+ ") "
#                         str_filter_dty += "  AND desg.pk_bint_id IN("+str(lst_desig)[1:-1]+ ") "
#                         str_filter_wkoff += "  AND desg.pk_bint_id IN("+str(lst_desig)[1:-1]+ ") "
#                     else:
#                         lst_desig = get_hierarchy([int_department_id], int_desig_id, [0,2],[])
#                         if not lst_desig and request.user.userdetails.fk_department.vchr_name != 'HR & ADMIN' and request.user.userdetails.fk_desig.vchr_name not in ['MANAGER - BUSINESS OPERATIONS']:
#                             conn.close()
#                             return Response({'status':'failed'})
#                         if request.user.userdetails.fk_department.vchr_name != 'HR & ADMIN' and request.user.userdetails.fk_desig.vchr_name not in ['MANAGER - BUSINESS OPERATIONS']:
#                             str_filter += " AND dept.pk_bint_id = "+str(int_department_id)+" AND desg.pk_bint_id IN("+str(lst_desig)[1:-1]+ ") "
#                             str_filter_dty += " AND dept.pk_bint_id = "+str(int_department_id)+" AND desg.pk_bint_id IN("+str(lst_desig)[1:-1]+ ") "
#                             str_filter_wkoff += " AND dept.pk_bint_id = "+str(int_department_id)+" AND desg.pk_bint_id IN("+str(lst_desig)[1:-1]+ ") "


#             """Employee filter"""
#             if request.data.get('lstSelectedEmpId'):
#                 lst_emp_id = request.data.get('lstSelectedEmpId')

#                 str_filter += " AND ud.user_ptr_id in("+str(lst_emp_id)[1:-1]+") "
#                 str_filter_dty += " AND ud.user_ptr_id in("+str(lst_emp_id)[1:-1]+") "
#                 str_filter_wkoff += " AND ud.user_ptr_id in("+str(lst_emp_id)[1:-1]+") "


#             dat_from = datetime.strptime(request.data.get('datLeaveFrom') , '%Y-%m-%d')
#             dat_to = datetime.strptime(request.data.get('datLeaveTo') , '%Y-%m-%d')
#             str_query = "SELECT le.pk_bint_id,le.dat_from,le.dat_to,le.vchr_reason,le.int_status,CONCAT(au.first_name,' ',CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(ud.vchr_middle_name,' ',au.last_name) ELSE au.last_name END) AS str_emp_name, ud.vchr_employee_code,ud.user_ptr_id, ud.json_physical_loc,desg.vchr_name,br.vchr_name,le.vchr_file,lt.vchr_name,CONCAT(auu.first_name,' ',CASE WHEN udd.vchr_middle_name IS NOT NULL THEN CONCAT(udd.vchr_middle_name,' ',auu.last_name) ELSE auu.last_name END) AS str_hier_name,jp.vchr_name, le.dat_approved FROM auth_user AS au JOIN user_details AS ud ON ud.user_ptr_id=au.id LEFT JOIN department AS dept ON dept.pk_bint_id=ud.fk_department_id LEFT JOIN job_position AS desg ON desg.pk_bint_id=ud.fk_desig_id LEFT JOIN branch AS br ON br.pk_bint_id = ud.fk_branch_id JOIN leave AS le ON le.fk_user_id=ud.user_ptr_id JOIN leave_type AS lt ON lt.pk_bint_id=le.fk_leave_type_id LEFT JOIN hierarchy_level AS hr ON hr.fk_designation_id = ud.fk_desig_id AND hr.int_status=1 AND hr.int_mode in (0,2) JOIN (auth_user AS auu JOIN user_details AS udd ON udd.user_ptr_id=auu.id AND auu.is_active=TRUE LEFT JOIN job_position jp ON jp.pk_bint_id = udd.fk_desig_id) ON hr.fk_reporting_to_id = udd.fk_desig_id  AND udd.json_physical_loc <@ ud.json_physical_loc WHERE le.dat_from<='"+str(dat_to)+"' AND le.dat_to>='"+str(dat_from)+"'"
#             rst_leave = conn.execute(str_query+str_filter).fetchall()
#             for dct_item in rst_leave:
#                 dct_data={}
#                 dct_data['bln_combo'] = False
#                 dct_data['int_id'] = dct_item[0]
#                 dct_data['int_days'] = (dct_item[2]-dct_item[1]).days + 1
#                 if dct_item[1] == dct_item[2]:
#                     dct_data['dat_from'] = dct_item[1].strftime('%d/%m/%Y')
#                 else:
#                     dct_data['dat_from'] = dct_item[1].strftime('%d/%m/%Y')
#                     dct_data['dat_to'] = dct_item[2].strftime('%d/%m/%Y')
#                 dct_data['str_reason'] = dct_item[3]
#                 dct_data['str_emp_name'] = dct_item[5]
#                 dct_data['str_emp_code'] = dct_item[6]
#                 dct_data['str_emp_degn'] = dct_item[9]
#                 dct_data['str_emp_branch'] = dct_item[10]
#                 dct_data['vchr_file'] = dct_item[11]
#                 dct_data['str_leave_type'] = dct_item[12]
#                 dct_data['str_hier_name'] = dct_item[13]
#                 dct_data['str_hier_degn'] = dct_item[14]
#                 if dct_item[4] == 1:
#                     dct_data['str_status'] = 'Pending'
#                 if dct_item[4] == 2:
#                     dct_data['str_status'] = 'Approved'
#                     dct_data['dat_approved'] = dct_item[15].strftime('%d/%m/%Y')
#                 if dct_item[4] == 3:
#                     dct_data['str_status'] = 'Rejected'
#                 if dct_item[4] == 4:
#                     dct_data['str_status'] = 'Cancelled'
#                 lst_leave.append(dct_data)
#             lst_combo = []
#             if  (str_leave_type == 'COMBO' and not int_type) or (not str_leave_type and not int_type):
#                 str_query = "SELECT  le.pk_bint_id,le.dat_leave,le.vchr_reason,CONCAT(au.first_name,' ',CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(ud.vchr_middle_name,' ',au.last_name) ELSE au.last_name END) AS str_emp_name, ud.vchr_employee_code,ud.user_ptr_id, ud.json_physical_loc,le.int_status, desg.vchr_name, br.vchr_name, CONCAT(auu.first_name,' ',CASE WHEN udd.vchr_middle_name IS NOT NULL THEN CONCAT(udd.vchr_middle_name,' ',auu.last_name) ELSE auu.last_name END) AS str_hier_name,jp.vchr_name, le.dat_approved FROM auth_user AS au JOIN user_details AS ud ON ud.user_ptr_id=au.id LEFT JOIN department AS dept ON dept.pk_bint_id=ud.fk_department_id LEFT JOIN job_position AS desg ON desg.pk_bint_id=ud.fk_desig_id JOIN combo_off_users AS le ON le.fk_user_id=ud.user_ptr_id LEFT JOIN branch AS br ON br.pk_bint_id = ud.fk_branch_id LEFT JOIN hierarchy_level AS hr ON hr.fk_designation_id = ud.fk_desig_id AND hr.int_status=1 AND hr.int_mode in (0,2) JOIN (auth_user AS auu JOIN user_details AS udd ON udd.user_ptr_id=auu.id AND auu.is_active=TRUE LEFT JOIN job_position jp ON jp.pk_bint_id = udd.fk_desig_id) ON hr.fk_reporting_to_id = udd.fk_desig_id AND udd.json_physical_loc <@ ud.json_physical_loc WHERE le.dat_leave BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"' "
#                 rst_leave = conn.execute(str_query+str_filter).fetchall()

#                 for dct_item in rst_leave:
#                     dct_data={}
#                     dct_data['bln_combo'] = True
#                     dct_data['int_id'] = dct_item[0]
#                     dct_data['int_days'] = 1
#                     dct_data['dat_from'] = dct_item[1].strftime('%d/%m/%Y')
#                     dct_data['str_reason'] = dct_item[2]
#                     dct_data['str_emp_name'] = dct_item[3]
#                     dct_data['str_emp_code'] = dct_item[4]
#                     dct_data['str_emp_degn'] = dct_item[8]
#                     dct_data['str_emp_branch'] = dct_item[9]
#                     dct_data['str_hier_name'] = dct_item[10]
#                     dct_data['str_hier_degn'] = dct_item[11]
#                     dct_data['dat_approved'] = dct_item[12]
#                     dct_data['str_leave_type'] = 'Combo Leave'
#                     if dct_item[7] == 1:
#                         dct_data['str_status'] = 'Pending'
#                     if dct_item[7] == 2:
#                         dct_data['str_status'] = 'Approved'
#                     if dct_item[7] == 3:
#                         dct_data['str_status'] = 'Rejected'

#                     lst_combo.append(dct_data)
#             lst_onduty = []
#             if  (str_leave_type == 'ONDUTY') or (not str_leave_type and not int_type):
#                 str_query = "SELECT od.pk_bint_id,od.dat_request, CONCAT(au.first_name,' ',CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(ud.vchr_middle_name,' ',au.last_name) ELSE au.last_name END) AS str_emp_name, ud.vchr_employee_code,ud.user_ptr_id, ud.json_physical_loc,desg.vchr_name,br.vchr_name,od.chr_day_type, od.vchr_remarks,CONCAT(au_on.first_name,' ',CASE WHEN ud_on.vchr_middle_name IS NOT NULL THEN CONCAT(ud_on.vchr_middle_name,' ',au_on.last_name) ELSE au_on.last_name END) AS str_approved_name,jp_apr.vchr_name, CONCAT(au_vrf.first_name,' ',CASE WHEN ud_vrf.vchr_middle_name IS NOT NULL THEN CONCAT(ud_vrf.vchr_middle_name,' ',au_vrf.last_name) ELSE au_vrf.last_name END) AS str_varified_name,jp_vrf.vchr_name, od.int_status,od.dat_approved,od.dat_verified FROM (auth_user AS au JOIN user_details AS ud ON ud.user_ptr_id=au.id LEFT JOIN department AS dept ON dept.pk_bint_id=ud.fk_department_id LEFT JOIN job_position AS desg ON desg.pk_bint_id=ud.fk_desig_id LEFT JOIN branch AS br ON br.pk_bint_id = ud.fk_branch_id) JOIN on_duty_request AS od ON od.fk_requested_id = ud.user_ptr_id LEFT JOIN (hierarchy_level hr JOIN job_position AS jp_apr ON jp_apr.pk_bint_id=hr.fk_reporting_to_id) ON hr.fk_designation_id=ud.fk_desig_id AND hr.int_status=1 AND hr.int_mode in (0,2) LEFT JOIN (auth_user AS au_on JOIN user_details ud_on ON ud_on.user_ptr_id=au_on.id AND au_on.is_active=TRUE) ON hr.fk_reporting_to_id = ud_on.fk_desig_id AND ud_on.json_physical_loc <@ ud.json_physical_loc LEFT JOIN (auth_user AS au_vrf JOIN user_details ud_vrf ON ud_vrf.user_ptr_id=au_vrf.id AND au_vrf.is_active=TRUE LEFT JOIN job_position AS jp_vrf ON jp_vrf.pk_bint_id=ud_vrf.fk_desig_id) ON od.fk_verified_id = ud_vrf.user_ptr_id WHERE od.dat_request BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"' "
#                 rst_leave = conn.execute(str_query+str_filter_dty+' GROUP BY od.pk_bint_id, od.dat_request,  au.first_name, ud.vchr_middle_name, au.last_name, ud.vchr_employee_code, ud.user_ptr_id,  ud.json_physical_loc, desg.vchr_name, br.vchr_name, od.chr_day_type,  od.vchr_remarks, au_on.first_name, ud_on.vchr_middle_name, au_on.last_name, jp_apr.vchr_name, au_vrf.first_name, ud_vrf.vchr_middle_name, au_vrf.last_name, jp_vrf.vchr_name,  od.int_status, od.dat_approved, od.dat_verified ORDER BY od.dat_request,ud.user_ptr_id').fetchall()
#                 for dct_item in rst_leave:
#                     dct_data={}
#                     dct_data['bln_combo'] = False
#                     dct_data['int_id'] = dct_item[0]
#                     dct_data['int_days'] = 1
#                     dct_data['dat_from'] = dct_item[1].strftime('%d/%m/%Y')
#                     dct_data['str_emp_name'] = dct_item[2]
#                     dct_data['str_emp_code'] = dct_item[3]
#                     dct_data['str_emp_degn'] = dct_item[6]
#                     dct_data['str_emp_branch'] = dct_item[7]
#                     dct_data['str_reason'] = dct_item[9]
#                     dct_data['str_leave_type'] = 'On Duty'
#                     if dct_item[14]==0:
#                         dct_data['str_hier_name'] = dct_item[10] if dct_item[10] != ' ' else '---'
#                         dct_data['str_hier_degn'] = dct_item[11]
#                         dct_data['str_status'] = 'Pending'
#                     elif dct_item[14]==1:
#                         dct_data['str_hier_name'] = dct_item[10]
#                         dct_data['str_hier_degn'] = dct_item[11]
#                         dct_data['dat_approved'] = dct_item[15].strftime('%d/%m/%Y') if dct_item[15] else ''
#                         dct_data['str_status'] = 'Approved'
#                     elif dct_item[14]==2:
#                         dct_data['str_hier_name'] = dct_item[12]
#                         dct_data['str_hier_degn'] = dct_item[13]
#                         dct_data['dat_approved'] = dct_item[16].strftime('%d/%m/%Y') if dct_item[15] else ''
#                         dct_data['str_status'] = 'Verified'
#                     elif dct_item[14]==-1:
#                         dct_data['str_hier_name'] = dct_item[12]
#                         dct_data['str_hier_degn'] = dct_item[13]
#                         dct_data['dat_approved'] = dct_item[16].strftime('%d/%m/%Y') if dct_item[15] else ''
#                         dct_data['str_status'] = 'Rejected'
#                     lst_onduty.append(dct_data)
#             lst_weekoff = []
#             if  (str_leave_type == 'WEEKOFF') or (not str_leave_type and not int_type):
#                 str_query  = "SELECT wklv.pk_bint_id, wklv.dat_from, wklv.dat_to, CONCAT(au.first_name, ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(ud.vchr_middle_name, ' ', au.last_name) ELSE au.last_name END) AS str_emp_name, ud.vchr_employee_code, ud.user_ptr_id, ud.json_physical_loc, desg.vchr_name str_desig, br.vchr_name str_branch, CASE WHEN au_vrf.id IS NULL THEN CONCAT(au_on.first_name, ' ', CASE WHEN ud_on.vchr_middle_name IS NOT NULL THEN CONCAT(ud_on.vchr_middle_name, ' ', au_on.last_name) ELSE au_on.last_name END) ELSE CONCAT(au_vrf.first_name, ' ', CASE WHEN ud_vrf.vchr_middle_name IS NOT NULL THEN CONCAT(ud_vrf.vchr_middle_name, ' ', au_vrf.last_name) ELSE au_vrf.last_name END) END AS str_authorise_name, CASE WHEN au_vrf.id IS NULL THEN jp_apr.vchr_name ELSE jp_vrf.vchr_name END str_authorise_desig, CASE WHEN wklv.dat_verified IS NULL THEN wklv.dat_approve ELSE wklv.dat_verified END dat_approve, CASE WHEN wklv.int_status = -1 THEN 'Rejected' WHEN wklv.int_status = 0 THEN 'Cancelled' WHEN wklv.int_status = 1 THEN 'Approval Pending' WHEN wklv.int_status = 2 THEN 'Verification Pending' WHEN wklv.int_status = 3 THEN 'Verified' END str_status FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id LEFT JOIN department AS dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position AS desg ON desg.pk_bint_id = ud.fk_desig_id LEFT JOIN branch AS br ON br.pk_bint_id = ud.fk_branch_id JOIN weekoff_leave wklv ON wklv.fk_employee_id = ud.user_ptr_id LEFT JOIN (hierarchy_level hr JOIN job_position AS jp_apr ON jp_apr.pk_bint_id = hr.fk_reporting_to_id) ON hr.fk_designation_id = ud.fk_desig_id AND hr.int_status = 1 AND hr.int_mode in (0, 2) JOIN (auth_user AS au_on JOIN user_details ud_on ON ud_on.user_ptr_id = au_on.id AND au_on.is_active = TRUE) ON hr.fk_reporting_to_id = ud_on.fk_desig_id AND ud_on.json_physical_loc <@ ud.json_physical_loc LEFT JOIN (auth_user AS au_vrf JOIN user_details ud_vrf ON ud_vrf.user_ptr_id = au_vrf.id AND au_vrf.is_active = TRUE LEFT JOIN job_position AS jp_vrf ON jp_vrf.pk_bint_id = ud_vrf.fk_desig_id) ON wklv.fk_verified_id = ud_vrf.user_ptr_id WHERE wklv.dat_from <= '"+str(dat_to)+"' AND wklv.dat_to>='"+str(dat_from)+"'"
#                 rst_leave = conn.execute(str_query+str_filter_wkoff).fetchall()
#                 for dct_item in rst_leave:
#                     dct_item = dict(dct_item)
#                     dct_data={}
#                     dct_data['bln_combo'] = False
#                     dct_data['int_id'] = dct_item['pk_bint_id']
#                     dct_data['int_days'] = (dct_item['dat_to']-dct_item['dat_from']).days + 1
#                     if dct_item['dat_from'] == dct_item['dat_to']:
#                         dct_data['dat_from'] = dct_item['dat_from'].strftime('%d/%m/%Y')
#                     else:
#                         dct_data['dat_from'] = dct_item['dat_from'].strftime('%d/%m/%Y')
#                         dct_data['dat_to'] = dct_item['dat_to'].strftime('%d/%m/%Y')
#                     dct_data['str_reason'] = ''
#                     dct_data['str_emp_name'] = dct_item['str_emp_name']
#                     dct_data['str_emp_code'] = dct_item['vchr_employee_code']
#                     dct_data['str_emp_degn'] = dct_item['str_desig']
#                     dct_data['str_emp_branch'] = dct_item['str_branch']
#                     dct_data['str_leave_type'] = 'Week Off'
#                     dct_data['str_hier_name'] = dct_item['str_authorise_name']
#                     dct_data['str_hier_degn'] = dct_item['str_authorise_desig']
#                     dct_data['dat_approved'] = dct_item['dat_approve'].strftime('%d/%m/%Y') if dct_item['dat_approve'] else ''
#                     dct_data['str_status'] = dct_item['str_status']
#                     lst_weekoff.append(dct_data)

#             if str_leave_type == 'COMBO':
#                 lst_leave = lst_combo
#             elif str_leave_type == 'WEEKOFF':
#                 lst_leave = lst_weekoff
#             elif str_leave_type == 'ONDUTY':
#                 lst_leave = lst_onduty
#             elif str_leave_type:
#                 lst_leave = lst_leave
#             else:
#                 lst_leave = lst_leave+lst_combo+lst_onduty+lst_weekoff
#             if lst_leave == []:
#                 conn.close()
#                 return Response({'status':1, 'lst_leave':lst_leave,'data':'No Data'})
#             file_name = 'LeaveReport/Leave_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
#             if path.exists(file_name):
#                 os.remove(file_name)
#             if not path.exists(settings.MEDIA_ROOT + '/LeaveReport/'):
#                 os.mkdir(settings.MEDIA_ROOT + '/LeaveReport/')
#             writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
#             workbook = writer.book
#             worksheet = workbook.add_worksheet()

#             title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
#             title_style.set_align('vcenter')
#             title_style.set_pattern(1)
#             title_style.set_bg_color('#ffe0cc')
#             worksheet.merge_range('A1:J1', 'Leave Report ('+dat_from.strftime('%d/%m/%Y')+' - '+dat_to.strftime('%d/%m/%Y')+')', title_style)
#             worksheet.set_row(0, 30)

#             head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
#             head_style.set_pattern(1)
#             head_style.set_bg_color('#bfbfbf')
#             head_style.set_align('vcenter')
#             worksheet.autofilter('B2:J2')

#             row_style = workbook.add_format({'font_size':11})
#             row_style.set_align('vcenter')

#             worksheet.protect('',{'autofilter':True})

#             int_row = 1
#             worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
#             worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
#             worksheet.write(int_row, 2, 'EMP NAME', head_style); worksheet.set_column(2, 2, 30)
#             worksheet.write(int_row, 3, 'BRANCH', head_style); worksheet.set_column(3, 3, 20)
#             worksheet.write(int_row, 4, 'DATE', head_style); worksheet.set_column(4, 4, 20)
#             worksheet.write(int_row, 5, 'TYPE', head_style); worksheet.set_column(5, 5, 15)
#             worksheet.write(int_row, 6, 'AUTHORIZING PERSON', head_style); worksheet.set_column(6, 6, 30)
#             worksheet.write(int_row, 7, 'AUTHORIZING DESIGNATION', head_style); worksheet.set_column(7, 7, 35)
#             worksheet.write(int_row, 8, 'DATE OF APPROVAL', head_style); worksheet.set_column(8, 8, 20)
#             worksheet.write(int_row, 9, 'STATUS', head_style); worksheet.set_column(9, 9, 13)
#             worksheet.set_row(int_row, 23)


#             for ins_data in lst_leave:
#                 int_row += 1
#                 worksheet.write(int_row, 0, int_row-1, row_style)
#                 worksheet.write(int_row, 1, ins_data.get('str_emp_code'), row_style)
#                 worksheet.write(int_row, 2, ins_data.get('str_emp_name'), row_style)
#                 worksheet.write(int_row, 3, ins_data.get('str_emp_branch'), row_style)
#                 worksheet.write(int_row, 4, ins_data.get('dat_from'), row_style)
#                 worksheet.write(int_row, 5, ins_data.get('str_leave_type'), row_style)
#                 worksheet.write(int_row, 6, ins_data.get('str_hier_name'), row_style)
#                 worksheet.write(int_row, 7, ins_data.get('str_hier_degn'), row_style)
#                 worksheet.write(int_row, 8, ins_data.get('dat_approved'), row_style)
#                 worksheet.write(int_row, 9, ins_data.get('str_status'), row_style)
#                 worksheet.set_row(int_row, 20, row_style)
#             writer.save()
#             conn.close()
#             return Response({'status':1, 'lst_leave':lst_leave,'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})


#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':'error'})


# class SetLeaveAPI(APIView):
#     def post(self,request):
#         try:
#             lst_emp_id = request.data.get('lstEmployee')
#             str_remarks = request.data.get('strRemark')
#             dat_expiry = datetime.strptime(request.data['datExpire'],'%Y-%m-%d')
#             if request.data.get('blnMarriage'):
#                 for int_id in lst_emp_id:
#                     str_name = UserDetails.objects.filter(id = int_id).annotate(full_name =Concat('first_name', V(' '),'last_name')).values('user_ptr_id','full_name','username')[0]['full_name']
#                     if SetLeave.objects.filter(fk_user_id = int_id, dat_expiry__gt=date.today(),int_status=0, fk_leave_type =LeaveType.objects.get(vchr_name='MARRIAGE LEAVE',int_year=date.today().year,bln_active = True)):
#                         return Response({'status':0, 'message':'Marriage Leave already assigned for '+str_name+''})
#                     if Leave.objects.filter(fk_user = int_id,fk_leave_type=LeaveType.objects.get(vchr_name='MARRIAGE LEAVE',int_year=date.today().year,bln_active = True)).values():
#                         return Response({'status':0, 'message':'Marriage Leave already taken by '+str_name+''})
#                 for int_id in lst_emp_id:
#                     SetLeave.objects.filter(fk_user_id = int_id, dat_expiry__lt=date.today(),int_status=0).update(int_status=2)
#                     SetLeave.objects.create(fk_user_id = int_id, fk_leave_type =LeaveType.objects.get(vchr_name='MARRIAGE LEAVE',int_year=date.today().year,bln_active = True),
#                                 dat_expiry=dat_expiry,vchr_remarks=str_remarks,int_status = 0,dat_created=datetime.now(),fk_created_id=request.user.id)
#             else:
#                 for int_id in lst_emp_id:
#                     str_name = UserDetails.objects.filter(id = int_id).annotate(full_name =Concat('first_name', V(' '),'last_name')).values('user_ptr_id','full_name','username')[0]['full_name']
#                     if SetLeave.objects.filter(fk_user_id = int_id, dat_expiry__gt=date.today(),int_status=0, fk_leave_type =LeaveType.objects.get(vchr_name='PARENTAL LEAVE',int_year=date.today().year,bln_active = True)):
#                         return Response({'status':0, 'message':'Parental Leave already assigned for '+str_name+''})
#                 for int_id in lst_emp_id:
#                     SetLeave.objects.filter(fk_user_id = int_id, dat_expiry__lt=date.today(),int_status=0).update(int_status=2)
#                     SetLeave.objects.create(fk_user_id = int_id, fk_leave_type =LeaveType.objects.get(vchr_name='PARENTAL LEAVE',int_year=date.today().year,bln_active = True),
#                                 dat_expiry=dat_expiry,vchr_remarks=str_remarks,int_status = 0,dat_created=datetime.now(),fk_created_id=request.user.id)
#             return Response({'status':1, 'message':'success'})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'message':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
