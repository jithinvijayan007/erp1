from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from enquiry.models import EnquiryMaster
from staff_rating.models import StaffRating

from POS import ins_logger
from datetime import datetime
# Create your views here.

class StaffRatingView(View):
    def get(self, request,hash=None, *args, **kwargs):
        try:
            if hash:
                ins_enquiry = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_hash = hash)
                ins_staff = StaffRating.objects.filter(fk_enquiry_master = ins_enquiry)
                str_company_name = str(ins_enquiry.fk_company.vchr_name).upper()
                str_branch_name = str(ins_enquiry.fk_branch.vchr_name).title()
                if ins_staff:
                    return render(request,template_name = 'sorry.html',context = {'company':str_company_name})
                else:
                    return render(request,template_name = 'staff_rating.html',context = {'branch':str_branch_name})
            else:
                return render(request,template_name = 'invalid_url.html')
        except ObjectDoesNotExist:
            return render(request,template_name = 'invalid_url.html')
        except Exception as e:
            ins_logger.logger.error(str(e))
            return HttpResponse('Error: '+str(e))
    def post(self, request,hash=None):
        if hash:
            ins_enquiry = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_hash = hash)
            dct_data = request.POST.dict()
            flt_rating = 0.0
            dct_data.pop('csrfmiddlewaretoken')

            # str_remarks = dct_data.get('remarks',' ')
            # enquiry_satisfaction = dct_data.get('enquirysatisfaction','yes')
            # staff_impression = dct_data.get('staffimpression','good')
            str_comments = dct_data.get('comments',' ')
            flt_rating = float(dct_data.get('star','2.0'))
            str_staff_attitude = dct_data.get('staffattitude','Extremely Satisfied')
            str_staff_knowledge = dct_data.get('staffknowledge','Extremely Satisfied')
            str_store_ambience = dct_data.get('storeambience','Extremely Satisfied')
            str_recommended = dct_data.get('recommended','yes')

            StaffRating.objects.create(
            vchr_comments = str_comments,
            dbl_rating = flt_rating,
            fk_enquiry_master = ins_enquiry,
            fk_user = ins_enquiry.fk_assigned,
            fk_customer = ins_enquiry.fk_customer,
            # vchr_staff_impression = staff_impression,
            # vchr_cust_satisfied = enquiry_satisfaction,
            dat_created = datetime.now(),
            vchr_staff_attitude = str_staff_attitude,
            vchr_staff_knowledge = str_staff_knowledge,
            vchr_store_ambience = str_store_ambience,
            vchr_recommended = str_recommended
            )
            return render(request,template_name = 'thankyou.html')
        else:
            return render(request,template_name = 'invalid_data.html')
