# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

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
    if request.method == 'POST':
        return _process_edit_submit(request, kpi)
#        return HttpResponse('Only get supported for the moment - Well done!')

    form = EditForm()
    page_title = 'Edit ' + kpi
    page_heading = 'Create / Edit KPI Dashboard'
    kpi_name = kpi


    context = {
        'form': form,
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
    }

    return render(request, 'summary/edit.html', context)


def _process_edit_submit(request, kpi):
    username = request.POST.get('username', None)
    secret = request.POST.get('secret', None)
    queue_url = request.POST.get('queue_url', None)
    queue_body = request.POST.get('queue_body', None)
    get_url = request.POST.get('get_url', None)
    get_body = request.POST.get('get_body', None)
    report_period_days = request.POST.get('report_period_days', None)

    print ('Username:', username)
    print ('Secret:', secret)
    print ('Queue URL:', queue_url)
    print ('kpi:', kpi)

    page_title = 'xyz' + kpi
    page_heading = 'abcd ' + username
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
        'result_status_message': 'All seems OK',
    }

    http_status = 200

    return render(request, 'summary/edit_confirmation.html', context, status=http_status)

