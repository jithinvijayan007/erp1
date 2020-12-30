from django.db.models import Q
from userdetails.models import UserLogDetails
from datetime import datetime
from userdetails.models import BackendUrls
from django.db.models import F
from re import sub
from rest_framework.authtoken.models import Token

# import geocoder
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

class InsertUserLog(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
    def __call__(self, request):
        # the view (and later middleware) are called.
        try:
                ins_backend_url = BackendUrls.objects.filter(vchr_backend_url=request.path).values('pk_bint_id','vchr_backend_url').first()

                if ins_backend_url:

                    jwt_authentication = JSONWebTokenAuthentication()
                    if jwt_authentication.get_jwt_value(request):
                        user, jwt = jwt_authentication.authenticate(request)

                    ins_userld = UserLogDetails.objects.filter(fk_module_id=ins_backend_url.get('pk_bint_id'),fk_user_id=user.id,dat_start_active__contains=datetime.today().date()).values('pk_bint_id').update(dat_last_active=datetime.now(),int_count=F('int_count')+1)

                    if not ins_userld:
                        UserLogDetails.objects.create(fk_module_id=ins_backend_url.get('pk_bint_id'),fk_user_id=user.id,dat_start_active=datetime.now(),dat_last_active=datetime.now(),int_count=1)

                    """Uncomment below code for getting location details(IP address) and place it above line 23

                    lst_userlocation = UserLogDetails.objects.filter(fk_user_id=request.user.id,dat_start_active__contains=datetime.today().date())
                    if lst_userlocation:
                        lst_userlocation = lst_userlocation.filter(fk_module_id=None,fk_user_id=request.user.id,dat_start_active__contains=datetime.today().date()).update(fk_module=ins_menu,int_count=1)
                        if not lst_userlocation:
                        """

        except Exception as e:
            pass
        response = self.get_response(request)
        return response
