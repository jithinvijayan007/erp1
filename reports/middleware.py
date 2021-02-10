from django.http import HttpResponse
from datetime import datetime
from django.conf import settings
from dateutil.tz import tzlocal
import pytz
import datetime as dt
# This contains the local timezone
local = tzlocal()
tz = pytz.timezone('Asia/Kolkata')
import json


class GetMaterializedView(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # import pdb;pdb.set_trace()
        try:
            if request.body.decode('utf-8'):
                if json.loads(request.body.decode('utf-8')).get('date_from','') and json.loads(request.body.decode('utf-8')).get('date_to',''):
                    fromdate= json.loads(request.body.decode('utf-8'))['date_from']
                    nowdate=datetime.now()
                    fd=datetime.strptime(fromdate,'%Y-%m-%d')
                    data=json.loads(request.body.decode('utf-8'))
                    # if json.loads(request.body.decode('utf-8'))['type']=='Enquiry':
                    #     lst_data1='mv_enquiry_data'
                    #     lst_data2='mv_enquiry_data_3month_back'
                    # elif json.loads(request.body.decode('utf-8'))['type']=='Sale':
                    #     lst_data1='mv_sales_data'
                    #     lst_data2='mv_sales_data_3month_back'

                    # Changed for sales report fix
                    lst_data1='mv_enquiry_data'
                    lst_data2='mv_enquiry_data_3month_back'

                    # lst_data1 = 'mv_enquiry_data'
                    if (nowdate-fd).days>90:
                        data['lst_mv']=[lst_data1,lst_data2]
                    else:
                        data['lst_mv']=[lst_data1]
                    request._body=json.dumps(data).encode('utf-8')
        except Exception as e:
            pass
        response = self.get_response(request)
        return response
