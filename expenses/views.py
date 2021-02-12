from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated,AllowAny

from company.models import CompanyDetails
from expenses.models import Expenses
from user_app.models import UserModel
from expenses.models import ExpensesCategory
from POS import ins_logger

from branch.models import Branch
# Create your views here.

from datetime import datetime
from .models import Payments

class AddExpensesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_category_id = int(request.data.get('category_id'))
            str_name = request.data.get('name')
            bln_recurring = request.data.get('recurring')
            int_company_id = int(request.data.get('company_id'))

            ins_expence = Expenses(fk_category=ExpensesCategory.objects.get(pk_bint_id=int_category_id),vchr_name = str_name,bln_recurring = bln_recurring,fk_company = CompanyDetails.objects.get(pk_bint_id = int_company_id),fk_branch=request.user.userdetails.fk_branch,bln_status = True)
            if bln_recurring:
                ins_expence.dat_expiry = request.data.get('dat_expiry')
                ins_expence.dbl_amount = request.data.get('dbl_amount')
            ins_expence.save()
            return JsonResponse({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':str(e)})

    def get(self,request):
        try:
            if request.GET.get('id'):
                lst_expenses = list(Expenses.objects.filter(pk_bint_id = int(request.GET.get('id')),bln_status = True,fk_company = request.user.userdetails.fk_company_id,fk_branch=request.user.userdetails.fk_branch).values('vchr_name','bln_recurring','pk_bint_id','dat_expiry','dbl_amount','fk_category','fk_category__vchr_category_name'))
            else:
                lst_expenses = list(Expenses.objects.filter(bln_status = True,fk_company = request.user.userdetails.fk_company_id,fk_branch=request.user.userdetails.fk_branch).values('vchr_name','bln_recurring','pk_bint_id','dat_expiry','dbl_amount','fk_category','fk_category__vchr_category_name'))
            return JsonResponse({'status':'success','data':lst_expenses})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':str(e)})

    def put(self,request):
        try:
            int_category_id = int(request.data.get('category_id'))
            str_name = request.data.get('name')
            bln_recurring = request.data.get('recurring')
            int_company_id = int(request.data.get('company_id'))
            int_id = int(request.data.get('pk_bint_id'))

            Expenses.objects.filter(pk_bint_id = int_id).update(
            fk_category = ExpensesCategory.objects.get(pk_bint_id=int_category_id),
            vchr_name = str_name,
            bln_recurring = bln_recurring,
            fk_company = CompanyDetails.objects.get(pk_bint_id = int_company_id),
            fk_branch=request.user.userdetails.fk_branch,
            dat_expiry = None,
            dbl_amount = None
            )
            if bln_recurring:
                Expenses.objects.filter(pk_bint_id = int_id).update(
                dat_expiry = request.data.get('dat_expiry'),
                dbl_amount = request.data.get('dbl_amount')
                )
            return JsonResponse({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':str(e)})


class DeleteExpenseAPIView(APIView):
    def post(self,request):
        permission_classes = [IsAuthenticated]
        try:
            Expenses.objects.filter(pk_bint_id = int(request.data.get('pk_bint_id'))).update(bln_status = False)
            return JsonResponse({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':str(e)})


class ViewCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            lst_category = list(ExpensesCategory.objects.values('pk_bint_id','vchr_category_name'))
            return JsonResponse({'status':'success','data':lst_category})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':str(e)})

class AddExpensesAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            vchr_doc_num=request.data.get('vchr_doc_num')
            dat_payment = request.data.get('dat_payment')
            ins_branch = Branch.objects.filter(vchr_code=request.data.get('vchr_branch_code')).first()
            if ins_branch:
               pass
            else:
               raise Exception('no branch exists in BI')


            int_amount = request.data.get('dbl_amount')
            vchr_expenses = request.data.get('vchr_expenses')

            Payments.objects.create(dat_payment=dat_payment,dbl_amount=int_amount,vchr_expenses=vchr_expenses,fk_branch=ins_branch,dat_created=datetime.now(),vchr_doc_num=vchr_doc_num)



            return JsonResponse({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': str(request.data.get('user'))})
            return Response({'status':'failed','data':str(e)})
