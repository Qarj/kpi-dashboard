# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Dash
from .forms import EditForm
from django.views.decorators.csrf import csrf_exempt

import random, json

def index(request):
    page_title = "KPI Dashboard"
    page_heading = "KPI Dashboard"
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
    }

    return render(request, 'summary/index.html', context)

def adobe(request):
    page_title = "Fake Adobe"
    page_heading = "Fake Adobe KPI endpoint"
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
    }

    return render(request, 'summary/adobe.html', context)

@csrf_exempt
def adobe_fake_api(request):
    if request.method != 'POST':
        return HttpResponse('Must be a post request')

    api_request = json.loads(request.body.decode("utf-8"))
    target_date = api_request['reportDescription']['date']

    random.seed(target_date)

    return HttpResponse('"visits":"' + str(random.randrange(100_000, 250_000)) + '"')

@csrf_exempt
def edit(request, kpi):
    try:
        dash = Dash.objects.get(kpi_name=kpi)
    except Dash.DoesNotExist:
        dash = Dash( kpi_name = kpi )
        dash.date_created = ''
        dash.date_modified = ''

    if request.method == 'POST':
        return _process_edit_submit(request, dash)

    secret_display = ''
    if dash.secret:
        secret_display = '********'

    form = EditForm()
    page_title = 'Edit ' + kpi
    page_heading = 'Create / Edit KPI Dashboard'

    context = {
        'form': form,
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
        'current_username': dash.username,
        'current_secret': secret_display,
        'current_queue_url': dash.queue_url,
        'current_queue_body': dash.queue_body,
        'current_get_url': dash.get_url,
        'current_get_body': dash.get_body,
        'current_date_created': dash.date_created,
        'current_date_modified': dash.date_modified,
        'current_report_period_days': dash.report_period_days,
    }

    return render(request, 'summary/edit.html', context)


def _process_edit_submit(request, dash):

    dash.username = request.POST.get('username', None)
    dash.queue_url = request.POST.get('queue_url', None)
    dash.queue_body = request.POST.get('queue_body', None)
    dash.get_url = request.POST.get('get_url', None)
    dash.get_body = request.POST.get('get_body', None)
    dash.report_period_days = request.POST.get('report_period_days', None)

    submitted_secret = request.POST.get('secret', None)
    if submitted_secret == '********':
        secret_message = 'API Secret not updated'
    else:
        dash.secret = submitted_secret
        secret_message = 'API Secret updated'

    dash.save()

#    print ('Username:', username)
#    print ('Secret:', secret)
#    print ('Queue URL:', queue_url)
#    print ('kpi:', kpi)

    page_title = 'xyz' + dash.kpi_name
    page_heading = 'abcd ' + dash.username
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
        'result_status_message': 'KPI config written to database ok',
        'secret_message': secret_message,
    }

    http_status = 200

    return render(request, 'summary/edit_confirmation.html', context, status=http_status)

