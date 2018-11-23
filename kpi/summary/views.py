# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Dash
from .forms import EditForm
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, date, timedelta
import random, json, hashlib, string, binascii

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


def table(request, kpi):

    page_title = kpi + ' table'

    try:
        dash = Dash.objects.get(kpi_name=kpi)
    except Dash.DoesNotExist:
        return render(request, 'summary/error.html', {'page_title': page_title, 'error_message': kpi + ' has not been defined'})

    debug = request.GET.get('debug', None)

    page_heading = str(dash.report_period_days) + ' days table view for KPI ' + kpi

    date_from = _kpi_date(dash.report_period_days)
    date_to = _kpi_date(1)
    dash.queue_body = dash.queue_body.replace('{DATE_FROM}', date_from).replace('{DATE_TO}', date_to)

    xwsse_header = _build_xwsse_header(dash.username, dash.secret)
    content_header = 'application/json'

    context = {
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
        'date_from': date_from,
        'date_to': date_to,
        'debug': debug,
        'queue_body': dash.queue_body,
        'xwsse_header': xwsse_header,
        'content_header': content_header,
    }

    return render(request, 'summary/table.html', context)

def _kpi_date(offset):
    desired_date = date.today() - timedelta(offset)
    return desired_date.strftime("%Y-%m-%d")

def _build_xwsse_header(username, secret):
    nonce = hashlib.md5(''.join(random.choices(string.ascii_uppercase + string.digits, k=42)).encode()).hexdigest()
    base64nonce = binascii.b2a_base64(binascii.a2b_qp(nonce))
    created_date = datetime.utcnow().isoformat() + 'Z'
    sha = nonce + created_date + secret
    sha_object = hashlib.sha1(sha.encode())
    password_64 = binascii.b2a_base64(sha_object.digest())

    properties = {
        "Username": username,
        "PasswordDigest": password_64.decode().strip(),
        "Nonce": base64nonce.decode().strip(),
        "Created": created_date,
    }
    header = 'UsernameToken ' + _serialize_header(properties)

    return header

def _serialize_header(properties):
    header = []
    for key, value in properties.items():
        header.append('{key}="{value}"'.format(key=key, value=value))
    return ', '.join(header)
