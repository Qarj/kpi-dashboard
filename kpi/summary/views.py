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
import time, random, json, hashlib, string, binascii

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
            queue.get_requests += 1
            queue.save()
        except Queue.DoesNotExist:
            #print ('REPORT_ID does not EXIST in Queue - EXCEPTION PROCESSING NEEDS IMPLEMENTATION')
            queue = Queue( report_id = '123456' )
            queue.metric_id = 'dummy_metric'
            queue.date_from = _get_aware_datetime_from_YYYY_MM_DD('2018-10-29')
            queue.date_to = _get_aware_datetime_from_YYYY_MM_DD('2018-10-30')
            queue.get_requests = 2
        if queue.get_requests < 2:
            return HttpResponse ( """
{
   "error":"report_not_ready",
   "error_description":"Report not ready",
   "error_uri":null
}
"""         )
        return HttpResponse( _build_metrics_response(queue.date_from, queue.date_to, queue.metric_id) )

    utc=pytz.UTC
    today_aware = utc.localize(datetime.today()) 

    if method == 'Report.Queue':
        report_id = str(random.randrange(1_000_000, 999_999_999))
        queue = Queue( report_id = report_id )
        queue.date_from = _get_aware_datetime_from_YYYY_MM_DD(api_request['reportDescription']['dateFrom'])
        queue.date_to = _get_aware_datetime_from_YYYY_MM_DD(api_request['reportDescription']['dateTo'])
        queue.metric_id = api_request['reportDescription']['metrics'][0]['id']
        queue.report_suite_id = api_request['reportDescription']['reportSuiteID']
        queue.date_granularity = api_request['reportDescription']['dateGranularity']
        queue.save()
        _remove_stale_queued_reports( today_aware - timedelta(minutes=10) )
        return HttpResponse( '{"reportID":' + report_id + '}' )

    if method == 'Report.Delete':
        report_id = api_request['reportID']
        queue = Queue.objects.get(report_id=report_id)
        try:
            queue = Queue.objects.get(report_id=report_id)
        except Queue.DoesNotExist:
            return HttpResponse( 'Cannot delete a report that does not exist' )
        queue.delete()
        return HttpResponse( 'Report deleted OK' )

    return HttpResponse( 'Unknown method ' + method + ', I only know Report.Get or Report.Queue' )

def _get_aware_datetime_from_YYYY_MM_DD(date_str):
    my_date = parse_datetime(date_str+'T12:00:00')
    if not is_aware(my_date):
        my_date = make_aware(my_date)
    return my_date

def _remove_stale_queued_reports(old_records):
    Queue.objects.filter( date_created__lte = old_records ).delete()

def _build_metrics_response(date_from, date_to, metric_id):
    count_data_template = """
         {
            "name":"{NAME_DATE}",
            "year":{YEAR},
            "month":{MONTH},
            "day":{DAY},
            "counts":[
               "{COUNT}"
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
         "id":"fake-adobe-analytics-api",
         "name":"Fake Adobe Analytics API"
      },
      "period":"{PERIOD_FROM_DATE} - {PERIOD_TO_DATE}",
      "metrics":[
         {
            "id":"{METRIC_ID}",
            "name":"{METRIC_NAME}",
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
         "{TOTAL}"
      ],
      "version":"1.4.18.10"
   },
   "waitSeconds":0,
   "runSeconds":0
}
"""
    delta = date_to - date_from
    counts_data = ''
    total = 0
    metric_date = date_from
    for i in range(1, delta.days+2):
        count = _random_count()
        total += int(count)
        count_data = count_data_template.replace( '{COUNT}', count )
        name_date = metric_date.strftime('%a. %d %b. %Y')
        year = metric_date.strftime('%Y')
        month = str(int(metric_date.strftime('%m')))
        day = str(int(metric_date.strftime('%d')))
        count_data = count_data.replace( '{NAME_DATE}', name_date )
        count_data = count_data.replace( '{YEAR}', year )
        count_data = count_data.replace( '{MONTH}', month )
        count_data = count_data.replace( '{DAY}', day )
        counts_data += count_data
        if i <= delta.days:
            counts_data += '        ,'
        metric_date += timedelta(1)

    period_from_date = date_from.strftime('%a. %d %b. %Y')
    period_to_date = date_to.strftime('%a. %d %b. %Y')

    metrics_response = metrics_response_template.replace('{COUNTS_DATA}', counts_data)
    metrics_response = metrics_response.replace('{TOTAL}', str(total))
    metrics_response = metrics_response.replace('{PERIOD_FROM_DATE}', period_from_date)
    metrics_response = metrics_response.replace('{PERIOD_TO_DATE}', period_to_date)
    metrics_response = metrics_response.replace('{METRIC_ID}', metric_id)
    metrics_response = metrics_response.replace('{METRIC_NAME}', metric_id.title())
    return metrics_response

def _random_count():
    return str( random.randrange(100_000, 270_000) )

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


def graph(request, kpi):

    page_title = kpi + ' graph'
    page_heading = kpi + ' graph'

    context = {
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
    }

    return render(request, 'summary/graph.html', context)


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
    external_request.add_header('X-WSSE', xwsse_header)
    external_request.add_header('Content-Type', content_header)
    queue_response_body = urlopen(external_request).read().decode()
#    print (queue_response_body)
    
    delay = 2
    if 'http://localhost' in dash.get_url:
        delay = 0 # Fake API always passes on second attempt
    for attempt in range(1,5):
        external_request = Request(dash.get_url, queue_response_body.encode('utf-8'))
        xwsse_header = _build_xwsse_header(dash.username, dash.secret)
        external_request.add_header('X-WSSE', xwsse_header)
        external_request.add_header('Content-Type', content_header)
        get_response_body = urlopen(external_request).read().decode()
        response_json = json.loads(get_response_body)
        if 'error' in response_json:
            if response_json['error'] == 'report_not_ready':
                time.sleep(delay)
                delay = delay * 2
        else:
            break

    number = 0
    metrics = []
    for datum in response_json['report']['data']:
        number += 1
        metrics.append ( {
            'number': str(number),
            'value': datum['counts'][0],
            'date': datum['name'],
        } )

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
        'metrics': metrics,
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
