import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from reminder.models import Reminder
# from datetime import datetime
from user_app.models import UserModel as AuthUser

# Create your views here.

class AddReminder(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_user = AuthUser.objects.get(user_ptr = request.user.id)
            title = request.data.get('title')
            description = request.data.get('description')
            ReminderDate = datetime.datetime.strptime(request.data['ReminderDate'],'%Y-%m-%dT%H:%M:%S.%fz')
            ReminderTime = request.data.get('ReminderTime')
            if not int_user:
                return Response({'status':'failed','data':'This user is not registered'})
            if not ReminderTime:
                dat_modified_reminder = ReminderDate.replace(hour=0,minute=0)
            else:
                dat_modified_reminder = ReminderDate.replace(hour=int(ReminderTime.split(':')[0]),minute=int(ReminderTime.split(':')[1]))
            int_reminderCount = Reminder.objects.filter(fk_user=int_user,dat_reminder__year=dat_modified_reminder.date().year\
                        ,dat_reminder__month=dat_modified_reminder.date().month,dat_reminder__day=dat_modified_reminder.date().day).count();

            ins_reminder = Reminder.objects.create(

                fk_user = int_user,
                dat_created_at =  datetime.datetime.now(),
                vchr_title=title,
                vchr_description = description,
                dat_reminder = dat_modified_reminder
                # vchr_time = ReminderTime,
                # vchr_time_period = ReminderPeriod
            )
            ins_reminder.save()
            return JsonResponse({'status':'success','count':int_reminderCount})
        except Exception as msg:
            return JsonResponse({'status':'failed'})

class ListReminder(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_user = AuthUser.objects.get(user_ptr = request.user.id)
            lst_reminder =list(Reminder.objects.filter(fk_user=int_user).values('pk_bint_id','dat_reminder','vchr_title'))
            return JsonResponse({'status':'success','data':lst_reminder})
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg) })
class ViewReminder(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            if not request.data.get('reminder_id'):
                return Response({'status':'failed','data':'please provide reminder id'})
            dct_reminder = Reminder.objects.filter(pk_bint_id=int(request.data.get('reminder_id'))).values()
            return Response({'status':'success','data':dct_reminder})
        except Exception as msg:
            return Response({'status':'failed','data':str(msg) })


# class UpdateReminder(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#
#             int_user = AuthUser.objects.get(user_ptr = int(request.data.get('user_id')))
#             int_pk_bint_id = int(request.data.get('pk_bint_id'))
#             vchr_title = request.data.get('title')
#             vchr_description = request.data.get('description')
#             ReminderDate = datetime.datetime.strptime(request.data['ReminderDate'],'%a %b %d %Y')
#             ReminderTime = request.data.get('ReminderTime')
#             if not request.data.get('user_id'):
#                 return Response({'status':'failed','data':'This user not registered'})
#             if not request.data.get('pk_bint_id'):
#                 return Response({'status':'failed','data':'Please provide request id'})
#             if not ReminderTime:
#                 dat_modified_reminder = ReminderDate.replace(hour=0,minute=0)
#             else:
#                 dat_modified_reminder = ReminderDate.replace(hour=int(ReminderTime.split(':')[0]),minute=int(ReminderTime.split(':')[1]))
#
#             int_reminderCount = Reminder.objects.filter(fk_user=int_user,dat_reminder__year=dat_modified_reminder.date().year\
#                         ,dat_reminder__month=dat_modified_reminder.date().month,dat_reminder__day=dat_modified_reminder.date().day).exclude(pk_bint_id=int_pk_bint_id).count();
#             # if int_reminderCount > 2:
#             #     return Response({'status':'failed','data':'You reached the limit in selected date','count':int_reminderCount})
#
#             ins_reminder = Reminder.objects.filter(pk_bint_id=int_pk_bint_id).\
#                     update(vchr_title=vchr_title,vchr_description=vchr_description,dat_reminder=dat_modified_reminder,dat_updated_at=datetime.datetime.now())
#             return JsonResponse({'status':'success','count':int_reminderCount})
#         except Exception as msg:
#             return JsonResponse({'status':'failed.0','data':str(msg) })
# class RemoveReminder(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#
#             if not request.data.get('user_id'):
#                 return Response({'status':'failed','data':'This user not registered'})
#             int_user = AuthUser.objects.get(user_ptr = int(request.data.get('user_id')))
#             if not request.data.get('pk_bint_id'):
#                 return Response({'status':'failed','data':'Please provide request id'})
#             int_pk_bint_id = int(request.data.get('pk_bint_id'))
#             ins_reminder = Reminder.objects.filter(pk_bint_id=int_pk_bint_id,).delete()
#             return JsonResponse({'status':'success'})
#         except Exception as msg:
#             return JsonResponse({'status':'failed','data':str(msg)})
