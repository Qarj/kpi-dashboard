# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Dash
from .models import Queue
from .forms import EditForm
from django.views.decorators.csrf import csrf_exempt

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from datetime import datetime, date, timedelta
import pytz
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
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

    method = request.GET.get('method', None)
    api_request = json.loads(request.body.decode("utf-8"))

    if method == 'Report.Get':
        report_id = api_request['reportID']
        try:
            queue = Queue.objects.get(report_id=report_id)
        except Queue.DoesNotExist:
            print ('REPORT_ID does not EXIST in Queue - EXCEPTION PROCESSING NEEDS IMPLEMENTATION')
            queue = Queue( report_id = '123456' )
            queue.metric = 'dummy_metric'
            queue.date_from = _get_aware_datetime_from_YYYY_MM_DD('2018-10-29')
            queue.date_to = _get_aware_datetime_from_YYYY_MM_DD('2018-10-30')
#        random.seed(report_id)
#        return HttpResponse( '{"visits":"' + str(random.randrange(100_000, 250_000)) + '"}' )
        return HttpResponse( _build_metrics_response(queue.date_from, queue.date_to, queue.metric_id) )

    utc=pytz.UTC
    today_aware = utc.localize(datetime.today()) 

    if method == 'Report.Queue':
        report_id = str(random.randrange(1_000_000, 999_999_999))
        queue = Queue( report_id = report_id )
        queue.date_from = _get_aware_datetime_from_YYYY_MM_DD(api_request['reportDescription']['dateFrom'])
        queue.date_to = _get_aware_datetime_from_YYYY_MM_DD(api_request['reportDescription']['dateTo'])
        queue_metric_id = api_request['reportDescription']['metrics'][0]['id']
        queue.report_suite_id = api_request['reportDescription']['reportSuiteID']
        queue.date_granularity = api_request['reportDescription']['dateGranularity']
        queue.save()
        _remove_stale_queued_reports( today_aware - timedelta(minutes=10) )
#        Queue.objects.filter( date_created__lte = today_aware - timedelta(minutes=10) ).delete()
#        random.seed(date_from)
        return HttpResponse( '{"reportID":' + report_id + '}' )

    return HttpResponse( 'Unknown method ' + method + ', I only know Report.Get or Report.Queue' )

def _get_aware_datetime_from_YYYY_MM_DD(date_str):
    my_date = parse_datetime(date_str+'T12:00:00')
    if not is_aware(my_date):
        my_date = make_aware(my_date)
    return my_date

def _remove_stale_queued_reports(old_records):
    Queue.objects.filter( date_created__lte = old_records ).delete()

def _build_metrics_response(date_from, date_to, metric_id):
    counts_data_template = """
         {
            "name":"Mon. 19 Nov. 2018",
            "year":2018,
            "month":11,
            "day":19,
            "counts":[
               "123456"
            ]
         }
"""
    metrics_response_template = """
{
   "report":{
      "type":"overtime",
      "elements":[
         {
            "id":"datetime",
            "name":"Date"
         }
      ],
      "reportSuite":{
         "id":"my-brand-id",
         "name":"Example Website"
      },
      "period":"Mon. 19 Nov. 2018 - Mon. 19 Nov. 2018",
      "metrics":[
         {
            "id":"visits",
            "name":"Visits",
            "type":"number",
            "decimals":0,
            "latency":1577,
            "current":false
         }
      ],
      "data":[
         {COUNTS_DATA}
      ],
      "totals":[
         "135010"
      ],
      "version":"1.4.18.10"
   },
   "waitSeconds":0,
   "runSeconds":0
}
"""
    delta = date_to - date_from
    print ('from, to, delta_days:', date_from, date_to, delta.days)
    counts_data = ''
    for i in range(1, delta.days+2):
        print ('i is now', i)
        counts_data += counts_data_template
        if i < delta.days:
            counts_data += '        ,'

    print ('counts_data is', counts_data)

#    counts_data = counts_data_template + ',' + counts_data_template
    metrics_response = metrics_response_template.replace('{COUNTS_DATA}', counts_data)
    return metrics_response

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

    external_request = Request(dash.queue_url, dash.queue_body.encode('utf-8'))
    queue_response_body = urlopen(external_request).read().decode()

#    external_request = Request(dash.get_url, dash.get_body.encode('utf-8'))
    external_request = Request(dash.get_url, queue_response_body.encode('utf-8'))
    get_response_body = urlopen(external_request).read().decode()

    context = {
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
        'date_from': date_from,
        'date_to': date_to,
        'debug': debug,
        'queue_url': dash.queue_url,
        'queue_body': dash.queue_body,
        'get_url': dash.get_url,
        'xwsse_header': xwsse_header,
        'content_header': content_header,
        'queue_response_body': queue_response_body,
        'get_response_body': get_response_body,
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
