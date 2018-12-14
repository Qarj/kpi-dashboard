# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Dash
from .models import Queue
from .models import Endpoint
from .models import Cache
from .forms import EditForm
from .forms import EndpointForm
from django.views.decorators.csrf import csrf_exempt

from urllib.parse import urlencode
import urllib.request
from urllib.request import Request, urlopen

from datetime import datetime, date, timedelta
from dateutil import parser
import pytz
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
import time, random, json, hashlib, string, binascii

QUEUE_BODY_TEMPLATE="""
{
    "reportDescription":{
        "reportSuiteID":"{REPORT_SUITE_ID}",
        "dateFrom":"{DATE_FROM}",
        "dateTo":"{DATE_TO}",
        "dateGranularity":"day",
        "metrics":[
            {
                "id":"{METRIC_ID}"
            }
        ]
    }
}
"""

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
"""         , status=400 )
        return HttpResponse( _build_metrics_response(queue.date_from, queue.date_to, queue.metric_id))

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

    form = EditForm()
    page_title = 'Edit ' + kpi
    page_heading = 'Create / Edit KPI Dashboard'

    context = {
        'form': form,
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
        'current_metric_id': dash.metric_id,
        'current_metric_desc': dash.metric_desc,
        'current_default_report_suite_id': dash.default_report_suite_id,
        'current_default_report_period_days': dash.default_report_period_days,
        'current_date_created': dash.date_created,
        'current_date_modified': dash.date_modified,
    }

    return render(request, 'summary/edit.html', context)


def _process_edit_submit(request, dash):

    dash.metric_id = request.POST.get('metric_id', None)
    dash.metric_desc = request.POST.get('metric_desc', None)
    dash.default_report_suite_id = request.POST.get('default_report_suite_id', None)
    dash.default_report_period_days = request.POST.get('default_report_period_days', None)

    dash.save()

    page_title = dash.kpi_name
    page_heading = dash.kpi_name
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
        'result_status_message': 'KPI config written to database ok',
    }

    http_status = 200

    return render(request, 'summary/edit_confirmation.html', context, status=http_status)


@csrf_exempt
def endpoint(request, type):
    try:
        endpoint = Endpoint.objects.get(endpoint_type=type)
    except Endpoint.DoesNotExist:
        endpoint = Endpoint( endpoint_type = type )
        endpoint.date_created = ''
        endpoint.date_modified = ''

    if request.method == 'POST':
        return _process_endpoint_submit(request, endpoint)

    secret_display = ''
    if endpoint.secret:
        secret_display = '********'

    form = EndpointForm()
    page_title = 'Endpoint ' + type
    page_heading = 'Create / Edit Adobe Analytics Endpoint'

    context = {
        'form': form,
        'endpoint_type': type,
        'page_title': page_title,
        'page_heading': page_heading,
        'current_username': endpoint.username,
        'current_secret': secret_display,
        'current_queue_url': endpoint.queue_url,
        'current_get_url': endpoint.get_url,
        'current_date_created': endpoint.date_created,
        'current_date_modified': endpoint.date_modified,
        'current_default_report_period_days': endpoint.default_report_period_days,
        'current_default_report_suite_id': endpoint.default_report_suite_id,
    }

    return render(request, 'summary/endpoint.html', context)


def _process_endpoint_submit(request, endpoint):

    endpoint.username = request.POST.get('username', None)
    endpoint.queue_url = request.POST.get('queue_url', None)
    endpoint.get_url = request.POST.get('get_url', None)
    endpoint.default_report_suite_id = request.POST.get('default_report_suite_id', None)
    endpoint.default_report_period_days = request.POST.get('default_report_period_days', None)

    submitted_secret = request.POST.get('secret', None)
    if submitted_secret == '********':
        secret_message = 'API Secret not updated'
    else:
        endpoint.secret = submitted_secret
        secret_message = 'API Secret updated'

    endpoint.save()

    page_title = 'xyz' + endpoint.endpoint_type
    page_heading = 'abcd ' + endpoint.username
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
        'result_status_message': 'Endpoint config written to database ok',
        'secret_message': secret_message,
    }

    http_status = 200

    return render(request, 'summary/endpoint_confirmation.html', context)


def graph(request, kpi, report_period_days=None, from_date=None, to_date=None):

    context = _get_data_for_kpi (request, kpi, 'graph', report_period_days, from_date, to_date)

    if 'error_message' in context:
        return render(request, 'summary/error.html', context)

    return render(request, 'summary/graph.html', context)


def table(request, kpi, report_period_days=None, from_date=None, to_date=None):

    context = _get_data_for_kpi (request, kpi, 'table', report_period_days, from_date, to_date)

    if 'error_message' in context:
        return render(request, 'summary/error.html', context)

    return render(request, 'summary/table.html', context)

def _get_data_for_kpi(request, kpi, view_type, report_period_days, url_from_date, url_to_date):

    page_title = kpi + ' ' + view_type

    endpoint_type = request.GET.get('endpoint', 'prod')

    try:
        endpoint = Endpoint.objects.get(endpoint_type=endpoint_type)
    except Endpoint.DoesNotExist:
        return _build_error_context(kpi, page_title, 'Endpoint ' + endpoint_type + ' has not been defined')

    endpoint_type = request.GET.get('endpoint', 'prod')
    debug = request.GET.get('debug', None)
    report_suite_id = request.GET.get('report_suite_id', None)

    if report_period_days is None:
        report_period_days = str(endpoint.default_report_period_days)
    if report_suite_id is None:
        report_suite_id = endpoint.default_report_suite_id
    metric_id = kpi

    if url_from_date is not None:
        date_from = _parse_date(url_from_date)
        date_to = _parse_date(url_to_date)
        page_heading = date_from + ' to ' + date_to + ' ' + view_type + ' view for KPI ' + kpi
    else:
        date_from = _kpi_date(int(report_period_days))
        date_to = _kpi_date(1)
        page_heading = report_period_days + ' days ' + view_type + ' view for KPI ' + kpi

    if _date_object_from_adobe_date(date_to) >= date.today():
        return _build_error_context(kpi, page_title, 'To date cannot be greater than yesterday')

    if _date_object_from_adobe_date(date_from) > _date_object_from_adobe_date(date_to):
        return _build_error_context(kpi, page_title, 'From date cannot be greater than to date')

    queue_body = QUEUE_BODY_TEMPLATE.replace('{DATE_FROM}', date_from).replace('{DATE_TO}', date_to)
    queue_body = queue_body.replace('{METRIC_ID}', metric_id)
    queue_body = queue_body.replace('{REPORT_SUITE_ID}', report_suite_id)

    xwsse_header = _build_xwsse_header(endpoint.username, endpoint.secret)
    content_header = 'application/json'

    external_request = Request(endpoint.queue_url, queue_body.encode('utf-8'))
    external_request.add_header('X-WSSE', xwsse_header)
    external_request.add_header('Content-Type', content_header)

    response_json = _get_metrics_from_cache(metric_id, report_suite_id, date_from, date_to, endpoint_type)
    queue_response_body = 'NA'
    get_response_body = 'Metric data found in cache'
    cache_miss = False

    if response_json is None:
        cache_miss = True
        try:
            queue_response_body = urlopen(external_request).read().decode()
        except urllib.error.HTTPError as err:
            error_body = err.read().decode().replace("\\/", "/") 
            return _build_error_context(kpi, page_title, str(err.code) + ' Report.Queue error:' + error_body)

        delay = 2
        if 'http://localhost' in endpoint.get_url:
            delay = 0 # Fake API always passes on second attempt
        for attempt in range(1,5):
            external_request = Request(endpoint.get_url, queue_response_body.encode('utf-8'))
            xwsse_header = _build_xwsse_header(endpoint.username, endpoint.secret)
            external_request.add_header('X-WSSE', xwsse_header)
            external_request.add_header('Content-Type', content_header)
            try:
                get_response_body = urlopen(external_request).read().decode()
            except urllib.error.HTTPError as err:
                error_body = err.read().decode()
                error_json = json.loads(error_body)
                if 'error' in error_json:
                    if error_json['error'] == 'report_not_ready':
                        time.sleep(delay)
                        delay = delay * 2
                        continue
                return _build_error_context(kpi, page_title, str(err.code) + ' Report.Get error:' + error_body)
            response_json = json.loads(get_response_body)

    number = 0
    graph_values = ''
    graph_dates = ''
    metrics = []
    for datum in response_json['report']['data']:
        number += 1
        metrics.append ( {
            'number': str(number),
            'value': datum['counts'][0],
            'date': datum['name'],
            'metric_date': date(datum['year'], datum['month'], datum['day']),
        } )
        graph_values += datum['counts'][0] + ', '
        graph_dates += '"' + str(datum['day']) + '/' + str(datum['month']) + '", '

    if cache_miss:
        _update_production_metric_cache(metrics, metric_id, report_suite_id, endpoint_type)

    context = {
        'kpi_name': kpi,
        'page_title': page_title,
        'page_heading': page_heading,
        'date_from': date_from,
        'date_to': date_to,
        'debug': debug,
        'queue_url': endpoint.queue_url,
        'queue_body': queue_body,
        'get_url': endpoint.get_url,
        'xwsse_header': xwsse_header,
        'content_header': content_header,
        'queue_response_body': queue_response_body,
        'get_response_body': get_response_body,
        'metrics': metrics,
        'graph_values': graph_values,
        'graph_dates': graph_dates,
    }

    return context

def _get_metrics_from_cache(metric_id, report_suite_id, date_from, date_to, endpoint_type):

    if endpoint_type != 'prod':
        return None

    metric_from_date = _date_object_from_adobe_date(date_from)
    metric_to_date = _date_object_from_adobe_date(date_to)

    if metric_from_date > metric_to_date:
        return None

    data = []
    process_date = metric_from_date
    while process_date <= metric_to_date: 
        try:
            cache = Cache.objects.get( metric_id=metric_id, report_suite_id=report_suite_id, metric_date=process_date )
        except Cache.DoesNotExist:
            return None
        counts = []
        counts.append (cache.value)
        data.append ( {
            'name': _adobe_api_datename_format(process_date),
            'year': process_date.year,
            'month': process_date.month,
            'day': process_date.day,
            'counts': counts,
        } )
        process_date = process_date + timedelta(days=1)

    response_json = { 'report': { 'data': data } }
    return response_json

def _update_production_metric_cache(metrics, metric_id, report_suite_id, endpoint_type):

    if endpoint_type != 'prod':
        return

    for metric in metrics:
        #metric_date = _date_object_from_adobe_date( metric.get('date') )
        metric_date = metric.get('metric_date')
        try:
            cache = Cache.objects.get( metric_id=metric_id, report_suite_id=report_suite_id, metric_date=metric_date )
        except Cache.DoesNotExist:
            cache = Cache( metric_id=metric_id, report_suite_id=report_suite_id, metric_date=metric_date )
        cache.value = metric.get('value')
        cache.save()
    return

def _kpi_date(offset):
    desired_date = date.today() - timedelta(offset)
    return _adobe_api_date_format(desired_date)

def _parse_date(url_date):
    desired_date = parser.parse(url_date)
    return _adobe_api_date_format(desired_date)

def _adobe_api_date_format(desired_date):
    return desired_date.strftime("%Y-%m-%d")

def _adobe_api_datename_format(desired_date):
    return desired_date.strftime('%a. %d %b. %Y')

def _date_object_from_adobe_date(adobe_date):
    return datetime.strptime(adobe_date, "%Y-%m-%d").date()

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

def _build_error_context(kpi, page_title, error_message):
    context = {
        'kpi_name': kpi,
        'page_title': page_title,
        'error_message': error_message,
    }
    return context
