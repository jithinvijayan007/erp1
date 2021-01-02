from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from company_permissions.models import GroupPermissions,SubCategory,MainCategory,CategoryItems,MenuCategory
from hierarchy.models import Hierarchy
from groups.models import Groups
from company.models import Company
from userdetails.models import UserDetails as Userdetails
from django.db.models import Value, BooleanField
from django.conf import settings
from dateutil.tz import tzlocal
import pytz
from django.http import JsonResponse
from django.db.models import Q
from POS import ins_logger
import sys, os
# Create your views here.

lst_route_disabled = []
lst_superuser_enabled = []



class SidebarAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        try:

            from collections import OrderedDict
            dct_sub_perms = OrderedDict()
            if not request.user.is_staff:
                ins_group_permissions = GroupPermissions.objects.filter(Q(Q(bln_add=True) | Q(bln_view=True) | Q(bln_edit=True) |Q(bln_delete=True)),fk_groups_id = request.user.userdetails.fk_group_id).values('fk_category_items_id','fk_category_items__fk_menu_category_id','fk_category_items__fk_sub_category_id','fk_category_items__fk_sub_category__vchr_icon_name','fk_category_items__fk_main_category_id','fk_category_items__fk_menu_category__vchr_menu_category_name','fk_category_items__fk_sub_category__vchr_sub_category_name','fk_category_items__fk_main_category__vchr_main_category_name','bln_add','bln_view','bln_edit','bln_edit','fk_category_items__fk_menu_category__vchr_addurl','fk_category_items__fk_menu_category__vchr_editurl','fk_category_items__fk_menu_category__vchr_viewurl','fk_category_items__fk_menu_category__vchr_listurl','fk_category_items__fk_menu_category__bln_has_children').order_by('fk_category_items__fk_main_category__int_main_category_order','fk_category_items__fk_sub_category__int_sub_category_order','fk_category_items__fk_menu_category__int_menu_category_order')

                for ins_per in ins_group_permissions:
                    if ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title() not in dct_sub_perms:
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()] = {}
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()] = {}
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['path'] = ''
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['title'] = ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['icon'] = ins_per['fk_category_items__fk_sub_category__vchr_icon_name']
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['class'] = 'has-arrow'
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['extralink'] = False
                        dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'] = []
                        if ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl'] and ins_per['fk_category_items__fk_menu_category__bln_has_children']:
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['fk_category_items__fk_menu_category__vchr_addurl'],
                                    'title': 'Add '+ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                        elif ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl']:
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['fk_category_items__fk_menu_category__vchr_addurl'],
                                    'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                        if ins_per['bln_view'] and ins_per['fk_category_items__fk_menu_category__vchr_listurl'] and ins_per['fk_category_items__fk_menu_category__bln_has_children']:
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['fk_category_items__fk_menu_category__vchr_listurl'],
                                    'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name']+' List',
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                        elif ins_per['bln_view'] and ins_per['fk_category_items__fk_menu_category__vchr_listurl']:
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['fk_category_items__fk_menu_category__vchr_listurl'],
                                    'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                    else:
                        if ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title() not in dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()]:
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()] = {}
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['path'] = ''
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['title'] = ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['icon'] = ins_per['fk_category_items__fk_sub_category__vchr_icon_name']
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['class'] = 'has-arrow'
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['extralink'] = False
                            dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'] = []
                            if ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl'] and ins_per['fk_category_items__fk_menu_category__bln_has_children']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_addurl'],
                                        'title': 'Add '+ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_addurl'],
                                        'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            if ins_per['bln_view'] and ins_per['fk_category_items__fk_menu_category__vchr_listurl'] and ins_per['fk_category_items__fk_menu_category__bln_has_children']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_listurl'],
                                        'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name']+' List',
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_view'] and ins_per['fk_category_items__fk_menu_category__vchr_listurl']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_listurl'],
                                        'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                        else:
                            if ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl'] and ins_per['fk_category_items__fk_menu_category__bln_has_children']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_addurl'],
                                        'title': 'Add '+ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_addurl'],
                                        'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            if ins_per['bln_view'] and ins_per['fk_category_items__fk_menu_category__vchr_listurl'] and ins_per['fk_category_items__fk_menu_category__bln_has_children']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_listurl'],
                                        'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name']+' List',
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_view'] and ins_per['fk_category_items__fk_menu_category__vchr_listurl']:
                                dct_sub_perms[ins_per['fk_category_items__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_category_items__fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['fk_category_items__fk_menu_category__vchr_listurl'],
                                        'title': ins_per['fk_category_items__fk_menu_category__vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )

            else:
                ins_group_permissions = MenuCategory.objects.filter().values('fk_sub_category__vchr_icon_name','vchr_menu_category_name','fk_sub_category__vchr_sub_category_name','fk_sub_category__fk_main_category__vchr_main_category_name','vchr_addurl','vchr_editurl','vchr_viewurl','vchr_listurl','bln_has_children').order_by('fk_sub_category__fk_main_category__int_main_category_order','fk_sub_category__int_sub_category_order','int_menu_category_order')
                for ins_per in ins_group_permissions:
                    ins_per['bln_view'] = True
                    ins_per['bln_add'] = True

                    if ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title() not in dct_sub_perms:
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()] = {}
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()] = {}
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['path'] = ''
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['title'] = ins_per['fk_sub_category__vchr_sub_category_name'].title()
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['icon'] = ins_per['fk_sub_category__vchr_icon_name']
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['class'] = 'has-arrow'
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['extralink'] = False
                        dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'] = []
                        if ins_per['bln_add'] and ins_per['vchr_addurl'] and ins_per['bln_has_children']:
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['vchr_addurl'],
                                    'title': 'Add '+ins_per['vchr_menu_category_name'],
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                        elif ins_per['bln_add'] and ins_per['vchr_addurl']:
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['vchr_addurl'],
                                    'title': ins_per['vchr_menu_category_name'],
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                        if ins_per['bln_view'] and ins_per['vchr_listurl'] and ins_per['bln_has_children']:
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['vchr_listurl'],
                                    'title': ins_per['vchr_menu_category_name']+' List',
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                        elif ins_per['bln_view'] and ins_per['vchr_listurl']:
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                {
                                    'path': ins_per['vchr_listurl'],
                                    'title': ins_per['vchr_menu_category_name'],
                                    'icon': 'mdi mdi-plus-outline',
                                    'class': '',
                                    'extralink': False,
                                    'submenu': []
                                }
                            )
                    else:
                        if ins_per['fk_sub_category__vchr_sub_category_name'].title() not in dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()]:
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()] = {}
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['path'] = ''
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['title'] = ins_per['fk_sub_category__vchr_sub_category_name'].title()
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['icon'] = ins_per['fk_sub_category__vchr_icon_name']
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['class'] = 'has-arrow'
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['extralink'] = False
                            dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'] = []
                            if ins_per['bln_add'] and ins_per['vchr_addurl'] and ins_per['bln_has_children']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_addurl'],
                                        'title': 'Add '+ins_per['vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_add'] and ins_per['vchr_addurl']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_addurl'],
                                        'title': ins_per['vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            if ins_per['bln_view'] and ins_per['vchr_listurl'] and ins_per['bln_has_children']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_listurl'],
                                        'title': ins_per['vchr_menu_category_name']+' List',
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_view'] and ins_per['vchr_listurl']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_listurl'],
                                        'title': ins_per['vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                        else:
                            if ins_per['bln_add'] and ins_per['vchr_addurl'] and ins_per['bln_has_children']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_addurl'],
                                        'title': 'Add '+ins_per['vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_add'] and ins_per['vchr_addurl']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_addurl'],
                                        'title': ins_per['vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            if ins_per['bln_view'] and ins_per['vchr_listurl'] and ins_per['bln_has_children']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_listurl'],
                                        'title': ins_per['vchr_menu_category_name']+' List',
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                            elif ins_per['bln_view'] and ins_per['vchr_listurl']:
                                dct_sub_perms[ins_per['fk_sub_category__fk_main_category__vchr_main_category_name'].title()][ins_per['fk_sub_category__vchr_sub_category_name'].title()]['submenu'].append(
                                    {
                                        'path': ins_per['vchr_listurl'],
                                        'title': ins_per['vchr_menu_category_name'],
                                        'icon': 'mdi mdi-plus-outline',
                                        'class': '',
                                        'extralink': False,
                                        'submenu': []
                                    }
                                )
                """add hierarchy data"""
                ins_sub_category = SubCategory.objects.filter(vchr_sub_category_name='ADD LOCATIONS').values('fk_main_category_id','vchr_icon_name','int_sub_category_order','vchr_sub_category_name','vchr_sub_category_value','pk_bint_id','fk_main_category_id__vchr_main_category_name').first()
                if ins_sub_category:
                    # import pdb; pdb.set_trace()

                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()] = {}
                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['path'] = ''
                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['title'] = ins_sub_category['vchr_sub_category_name'].title()
                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['icon'] = ins_sub_category['vchr_icon_name']
                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['class'] = 'has-arrow'
                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['extralink'] = False
                    dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['submenu'] = []
                    # if ins_per['bln_add'] and ins_per['fk_category_items__fk_menu_category__vchr_addurl']:
                    ins_hierarachy = Hierarchy.objects.exclude(vchr_name='BRANCH').values('vchr_name').order_by('-int_level')
                    for ins_data in ins_hierarachy:
                        dct_sub_perms[ins_sub_category['fk_main_category_id__vchr_main_category_name'].title()][ins_sub_category['vchr_sub_category_name'].title()]['submenu'].append(
                            {
                                'path': 'hierarchy/add',
                                'title': 'Add '+ins_data['vchr_name'].title(),
                                'icon': 'mdi mdi-plus-outline',
                                'class': '',
                                'extralink': False,
                                'submenu': []
                            }
                        )
            for ins_data in  dct_sub_perms:
                dct_sub_perms[ins_data] = dct_sub_perms[ins_data].values()
            dct_data = {}
            dct_data['data'] = dct_sub_perms
            return Response(dct_data)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
