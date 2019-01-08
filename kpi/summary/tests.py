# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from datetime import date, timedelta
import json, re

#
# Test Helpers
#

# https://stackoverflow.com/questions/4995279/including-a-querystring-in-a-django-core-urlresolvers-reverse-call
def my_reverse(viewname, kwargs=None, query_kwargs=None):
    """
    Custom reverse to add a query string after the url
    Example usage:
    url = my_reverse('my_test_url', kwargs={'pk': object.id}, query_kwargs={'next': reverse('home')})
    """
    url = reverse(viewname, kwargs=kwargs)

    if query_kwargs:
        return u'%s?%s' % (url, urlencode(query_kwargs))

    return url

def kpi_date(offset):
    desired_date = date.today() + timedelta(offset)
    return desired_date.strftime("%Y-%m-%d")

#target_date = '9999-99-99'
    
def build_report_queue_request_body(from_date, to_date):
    return \
{
    "reportDescription":{
        "reportSuiteID":"fake-adobe-suite-id",
        "dateFrom":from_date,
        "dateTo":to_date,
        "dateGranularity":"day",
        "metrics":[
            {
                "id":"visits"
            }
        ]
    }
}

def build_report_get_request_body(report_id):
    return \
{
    "reportID":report_id
}

class KPIIndexViewTests(TestCase):
    def test_index(self):
        """
        KPI index page exists
        """
        response = self.client.get(reverse('summary:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'KPI Dashboard')
    
class KPISummaryTests(TestCase):

    #
    # test helpers
    #

    def get_graph(self, debug=False, kpi='unknown', page_debug='true', report_period_days=None, from_date=None, to_date=None, endpoint='test', report_suite_id=None):
        return self._get_url( self._build_metric_display_url(kpi, page_debug, 'summary:graph', endpoint, report_period_days, from_date, to_date, report_suite_id), debug)

    def get_table(self, debug=False, kpi='unknown', page_debug='true', report_period_days=None, from_date=None, to_date=None, endpoint='test', report_suite_id=None):
        return self._get_url( self._build_metric_display_url(kpi, page_debug, 'summary:table', endpoint, report_period_days, from_date, to_date, report_suite_id), debug )

    def _build_metric_display_url(self, kpi, page_debug, target_view, endpoint, report_period_days, from_date, to_date, report_suite_id):
        kwargs={}
        kwargs['kpi'] = kpi
        if report_period_days is not None:
            kwargs['report_period_days'] = report_period_days
        if from_date is not None:
            kwargs['from_date'] = from_date
        if to_date is not None:
            kwargs['to_date'] = to_date
        query_kwargs={}
        query_kwargs['debug'] =  page_debug
        query_kwargs['endpoint'] =  endpoint
        if report_suite_id is not None:
            query_kwargs['report_suite_id'] =  report_suite_id
        return my_reverse(target_view, kwargs=kwargs, query_kwargs=query_kwargs)

    def get_edit(self, debug=False, kpi='unknown'):
        return self._get_url( self._build_edit_url(kpi), debug )

    def get_endpoint(self, debug=False, type='unknown'):
        return self._get_url( self._build_endpoint_url(type), debug )

    def _build_endpoint_url(self, type):
        kwargs={}
        kwargs['type'] = type
        return my_reverse('summary:endpoint', kwargs=kwargs)

    def _build_edit_url(self, kpi):
        kwargs={}
        kwargs['kpi'] = kpi
        return my_reverse('summary:edit', kwargs=kwargs)

    def submit_edit(self, kpi, metric_id='default_id', metric_desc='Default Desc', default_report_suite_id='default-suite', default_report_period_days=7,
                    debug=False):
        body = {
                    'metric_id': metric_id,
                    'metric_desc': metric_desc,
                    'default_report_suite_id': default_report_suite_id,
                    'default_report_period_days': default_report_period_days,
        }
        return self._post_url_and_body( self._build_edit_url(kpi), body, debug=debug )

    def submit_endpoint(self, type, username='default_username', default_report_period_days=7, secret='default_secret',
                    queue_url='http://localhost/kpi/summary/adobe_fake_api/?method=Report.Queue',
                    get_url='http://localhost/kpi/summary/adobe_fake_api/?method=Report.Get',
                    default_report_suite_id='test-suite-id',
                    debug=False):
        body = {
                    'username': username,
                    'secret': secret,
                    'queue_url': queue_url,
                    'get_url': get_url,
                    'default_report_suite_id': default_report_suite_id,
                    'default_report_period_days': default_report_period_days,
        }
        return self._post_url_and_body( self._build_endpoint_url(type), body, debug=debug )

    def adobe_fake_api(self, body, debug=False, method=''):
        my_date = '8888-88-88'
        return self._post_url_and_json_body( self._build_adobe_fake_api_url(method), body, debug )

    def _build_adobe_fake_api_url(self, method):
        kwargs={}
        if (method):
            kwargs['method'] = method
        return my_reverse('summary:adobe_fake_api', query_kwargs=kwargs)

    def _get_url(self, url, debug=False):
        response = self.client.get(url)
        if (debug):
            print('\nDebug URL:', url)
            print(response.content.decode('utf-8'), '\n')
        return response

    def _post_url_and_body(self, url, body, debug=False):
        postbody = body
        if (debug):
            print('\nDebug URL :', url)
            print('\nDebug Body:', postbody)
        response = self.client.post(url, body)
        if (debug):
            print('\nDebug Response Content Start\n', response.content.decode('utf-8'), '\n')
            print('\nDebug Response Content End\n')
        return response

    def _post_url_and_json_body(self, url, body, debug=False):
        postbody = json.dumps(body)
        if (debug):
            print('\nDebug URL :', url)
            print('\nDebug Body:', postbody)
        response = self.client.generic('POST', url, postbody)
        if (debug):
            print('\nDebug Response Content Start\n', response.content.decode('utf-8'), '\n')
            print('\nDebug Response Content End\n')
        return response

    def _assertRegex(self, response, regex):
        self.assertRegex(response.content.decode('utf-8'), regex)

    def _assertNotRegex(self, response, regex):
        self.assertNotRegex(response.content.decode('utf-8'), regex)

    def _assertCount(self, response, string, expectCount):
        actualCount = response.content.decode('utf-8').count(string)
        message = 'Expected to find ' + string + ' ' + str(expectCount) + ' times, but found ' + str(actualCount) + ' times'
        self.assertEqual(expectCount, actualCount, msg=message)


    #
    # Tests start here
    #

    #
    # Fake Adobe endpoint
    #

    def test_adobe_fake_api_info_page_exists(self):
        response = self.client.get(reverse('summary:adobe'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fake Adobe KPI endpoint')

    def test_adobe_fake_api_returns_JSON_on_POST_method_report_queue(self):
        response = self.adobe_fake_api(build_report_queue_request_body(kpi_date(-2),kpi_date(-1)), method='Report.Queue', debug=False)
        self._assertRegex(response, r'"\w+":')

    def test_adobe_fake_api_returns_JSON_on_POST_method_report_get(self):
        response = self.adobe_fake_api(build_report_get_request_body(12345), method='Report.Get', debug=False)
        self._assertRegex(response, r'"\w+":')

    def test_adobe_fake_api_returns_message_on_GET(self):
        response = self.client.get(reverse('summary:adobe_fake_api'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Must be a post request')

    def test_adobe_fake_api_report_queue_returns_reportID(self):
        response = self.adobe_fake_api(build_report_queue_request_body(kpi_date(-2),kpi_date(-1)), method='Report.Queue', debug=False)
        self._assertRegex(response, r'{"reportID":\d+}')

    def test_adobe_fake_api_returns_random_visits_greater_than_100k(self):
        response = self.adobe_fake_api(build_report_get_request_body(12345), method='Report.Get', debug=False)
        self._assertRegex(response, r'"counts":\[\s*"\d{5,}"')

    def test_adobe_fake_api_returns_message_when_method_unknown(self):
        response = self.adobe_fake_api(build_report_get_request_body(12345), method='Report.Sing', debug=False)
        self.assertContains(response, 'Unknown method')

    def test_adobe_fake_api_returns_metrics_response_body_similar_to_real_one(self):
        response = self.adobe_fake_api(build_report_get_request_body(12345), method='Report.Get', debug=False)
        self.assertContains(response, '"metrics":[')

    def test_adobe_fake_api_returns_metric_id(self):
        response = self.adobe_fake_api(build_report_get_request_body(12345), method='Report.Get', debug=False)
        self.assertContains(response, 'dummy_metric')

    def test_adobe_fake_api_returns_metric_name(self):
        response = self.adobe_fake_api(build_report_get_request_body(12345), method='Report.Get', debug=False)
        self.assertContains(response, 'Dummy_Metric')

    def test_adobe_fake_api_can_delete_queued_reports(self):
        response = self.adobe_fake_api(build_report_queue_request_body(kpi_date(-2),kpi_date(-1)), method='Report.Queue', debug=False)
        response_json = json.loads(response.content.decode('utf-8'))
        report_id = response_json['reportID']
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Get', debug=False)
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Get', debug=False)
        self._assertNotRegex(response, 'Dummy_Metric')
        self._assertRegex(response, r'"counts":\[\s*"\d{5,}"')
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Delete', debug=False)
        self.assertContains(response, 'Report deleted OK')
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Get', debug=False)
        self.assertContains(response, 'Dummy_Metric')

    def test_adobe_fake_api_returns_report_not_ready_on_first_attempt(self):
        response = self.adobe_fake_api(build_report_queue_request_body(kpi_date(-2),kpi_date(-1)), method='Report.Queue', debug=False)
        response_json = json.loads(response.content.decode('utf-8'))
        report_id = response_json['reportID']
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Get', debug=False)
        self._assertRegex(response, 'report_not_ready')
        self.assertEqual(400, response.status_code, 'Response code 400 not found, was ' + str(response.status_code))

    def test_adobe_fake_api_returns_report_on_second_attempt(self):
        response = self.adobe_fake_api(build_report_queue_request_body(kpi_date(-2),kpi_date(-1)), method='Report.Queue', debug=False)
        response_json = json.loads(response.content.decode('utf-8'))
        report_id = response_json['reportID']
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Get', debug=False)
        response = self.adobe_fake_api(build_report_get_request_body(report_id), method='Report.Get', debug=False)
        self._assertRegex(response, r'"counts":\[\s*"\d{5,}"')

    #
    # Create / Edit KPI form
    #

    def test_can_get_kpi_edit_page(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'Create / Edit KPI Dashboard')
        self.assertContains(response, 'Edit site_visits')
        self.assertContains(response, 'KPI Name')
        self.assertContains(response, '>site_visits<')

    def test_edit_page_form_has_default_report_period_days(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'default_report_period_days')
        self.assertContains(response, 'Default Report Period Days')
        self.assertContains(response, 'type="number" min="1" max="366"')

    def test_edit_page_form_has_default_report_suite_id(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'default_report_suite_id')
        self.assertContains(response, 'Default Report Suite Id')

    def test_edit_page_form_has_metric_id(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'metric_id')
        self.assertContains(response, 'Metric Id')

    def test_edit_page_form_has_metric_desc(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'metric_desc')
        self.assertContains(response, 'Metric Description')

    def test_edit_page_form_has_blank_date_created(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'date_created')
        self.assertContains(response, 'Date Created')
        self.assertContains(response, 'id="id_date_created"><') # is blank

    def test_edit_page_form_has_blank_date_modified(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'date_modified')
        self.assertContains(response, 'Date Modified')
        self.assertContains(response, 'id="id_date_modified"><') # is blank

    def test_can_submit_edit_dashboard_form_for_new_kpi(self):
        response = self.submit_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'KPI config written to database ok')

    def test_default_report_period_days_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', default_report_period_days='27', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '"27"')

    def test_default_report_suite_id_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', default_report_suite_id='my-report-suite', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '"my-report-suite"')

    def test_metric_id_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', metric_id='my_metric', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '"my_metric"')

    def test_metric_desc_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', metric_desc='My Metric Desc', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '"My Metric Desc"')

    def test_date_created_visible_on_subsequent_form_get(self):
        response = self.submit_edit(kpi='created', debug=False)
        response = self.get_edit(kpi='created', debug=False)
        self._assertRegex(response, r'date_created">\w+\. \d+, \d{4,4}')

    def test_date_modified_visible_on_subsequent_form_get(self):
        response = self.submit_edit(kpi='visible', debug=False)
        response = self.get_edit(kpi='visible', debug=False)
        self._assertRegex(response, r'date_modified">\w+\. \d+, \d{4,4}')


    #
    # Get KPI data in table view
    #

    def test_get_kpi_table_heading(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='table', debug=False)
        self.assertContains(response, 'table view for KPI table')

    def test_get_kpi_table_title(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='title', debug=False)
        self.assertContains(response, 'title table')

    def test_get_kpi_table_num_days(self):
        response = self.submit_endpoint(type='test', default_report_period_days='7', debug=False)
        response = self.get_table(kpi='title', debug=False)
        self.assertContains(response, '7 days table view')

    def test_get_kpi_table_datefrom(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='range', debug=False)
        self.assertContains(response, 'dateFrom">' + kpi_date(-2))

    def test_get_kpi_table_dateto(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='range', debug=False)
        self.assertContains(response, 'dateTo">' + kpi_date(-1))

    def test_get_kpi_table_dateto(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='range', debug=False)
        self.assertContains(response, 'dateTo">' + kpi_date(-1))

    def test_get_kpi_table_debug_info_only_shown_in_debug_mode(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='debug', page_debug='false', debug=False)
        self._assertNotRegex(response, r'dateFrom')

    def test_get_kpi_table_shows_substituted_report_queue_body(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='queue_body', debug=False)
        self.assertContains(response, 'dateGranularity')
        self.assertContains(response, 'dateFrom":"' + kpi_date(-2))

    def test_get_kpi_table_shows_x_wsse_header_in_debug_mode(self):
        response = self.submit_endpoint(type='test', username='my:user', debug=False)
        response = self.get_table(kpi='x-wsse_username', debug=False)
        self.assertContains(response, 'Username=&quot;my:user&quot;')
        self.assertContains(response, 'PasswordDigest=')
        self.assertContains(response, 'Nonce=')
        self.assertContains(response, 'Created=')

    def test_get_kpi_table_shows_content_type_header_in_debug_mode(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='content_type', debug=False)
        self.assertContains(response, 'application/json')

    def test_get_kpi_table_shows_queue_url_in_debug_mode(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='queue_url', debug=False)
        self.assertContains(response, 'method=Report.Queue')

    def test_get_kpi_table_shows_get_url_in_debug_mode(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='get_url', debug=False)
        self.assertContains(response, 'method=Report.Get')

    def test_get_kpi_table_shows_message_when_endpoint_not_defined(self):
        response = self.get_table(endpoint='unknown_endpoint', debug=False)
        self.assertContains(response, 'unknown_endpoint has not been defined')

    def test_get_kpi_table_shows_queue_post_response_in_debug_mode(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='queue_post', debug=False)
        self._assertRegex(response, r'reportID":\d+')

    def test_get_kpi_table_shows_get_post_response_in_debug_mode(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_table(kpi='queue_get', debug=False)
        self._assertRegex(response, r'counts":\[\s*"\d{5,}')

    def test_get_kpi_table_has_multiple_counts_in_get_report_1(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='multi', debug=False)
        self._assertCount(response, '"counts"', 2)

    def test_get_kpi_table_has_multiple_counts_in_get_report_2(self):
        response = self.submit_endpoint(type='test', default_report_period_days='3', debug=False)
        response = self.get_table(kpi='multi', debug=False)
        self._assertCount(response, '"counts"', 3)

    def test_get_kpi_table_has_different_counts_for_each_day(self):
        response = self.submit_endpoint(type='test', default_report_period_days='3', debug=False)
        response = self.get_table(kpi='different', debug=False)
        match = re.search(r'counts":\[\s*"(\d+)', response.content.decode('utf-8'))
        capture = match.group(1)
        self._assertCount(response, capture, 2) # in twice - once in raw response data, once in main table

    def test_get_kpi_table_total_is_sum_of_counts(self):
        response = self.submit_endpoint(type='test', default_report_period_days='3', debug=False)
        response = self.get_table(kpi='different', debug=False)
        total = 0
        for match in re.finditer(r'counts":\[\s*"(\d+)', response.content.decode('utf-8')):
            capture = match.group(1)
            total += int(capture)
        self._assertCount(response, str(total), 1)

    def test_get_kpi_table_period_from_date_is_correct(self):
        response = self.submit_endpoint(type='test', default_report_period_days='3', debug=False)
        period_from_date = date.today() - timedelta(3)
        period_from_date_string = period_from_date.strftime('%a. %d %b. %Y') # Mon. 19 Nov. 2018
        response = self.get_table(kpi='period_from', debug=False)
        self.assertContains(response, period_from_date_string)

    def test_get_kpi_table_period_to_date_is_correct(self):
        response = self.submit_endpoint(type='test', default_report_period_days='3', debug=False)
        period_to_date = date.today() - timedelta(1)
        period_to_date_string = period_to_date.strftime('%a. %d %b. %Y') # Wed. 21 Nov. 2018
        response = self.get_table(kpi='period_to', debug=False)
        self.assertContains(response, period_to_date_string)

    def test_get_kpi_table_data_name_date_is_correct(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        date_1 = date.today() - timedelta(2)
        date_2 = date.today() - timedelta(1)
        date_1_string = date_1.strftime('%a. %d %b. %Y') # Tue. 20 Nov. 2018
        date_2_string = date_2.strftime('%a. %d %b. %Y') # Wed. 21 Nov. 2018
        response = self.get_table(kpi='data_name_date', debug=False)
        self.assertContains(response, 'name":"' + date_1_string)
        self.assertContains(response, 'name":"' + date_2_string)

    def test_get_kpi_table_data_year_month_day_is_correct(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        date_1 = date.today() - timedelta(2)
        date_2 = date.today() - timedelta(1)
        date_1_year = date_1.strftime('%Y') # 2018
        date_1_month = str(int(date_1.strftime('%m'))) # lose leading zero
        date_1_day = str(int(date_1.strftime('%d'))) # lose leading zero
        date_2_year = date_1.strftime('%Y') # 2018
        date_2_month = str(int(date_1.strftime('%m'))) # lose leading zero
        date_2_day = str(int(date_1.strftime('%d'))) # lose leading zero
        response = self.get_table(kpi='data_date', debug=False)
        self.assertContains(response, 'year":' + date_1_year)
        self.assertContains(response, 'month":' + date_1_month)
        self.assertContains(response, 'day":' + date_1_day)
        self.assertContains(response, 'year":' + date_2_year)
        self.assertContains(response, 'month":' + date_2_month)
        self.assertContains(response, 'day":' + date_2_day)

    def test_get_kpi_table_data_metric_id_is_correct(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='data_date', debug=False)
        self.assertContains(response, 'id":"data_date')

    def test_get_kpi_table_data_metric_name_is_correct(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='data_date', debug=False)
        self.assertContains(response, 'name":"Data_Date')

    def test_get_kpi_table_shows_kpi_value_for_each_day(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        date_1 = date.today() - timedelta(2)
        date_2 = date.today() - timedelta(1)
        date_1_string = date_1.strftime('%a. %d %b. %Y') # Tue. 20 Nov. 2018
        date_2_string = date_2.strftime('%a. %d %b. %Y') # Wed. 21 Nov. 2018
        response = self.get_table(kpi='each_day', debug=False)
        self.assertContains(response, 'metric_date_1">' + date_1_string)
        self.assertContains(response, 'metric_date_2">' + date_2_string)
        counts = []
        for match in re.finditer(r'counts":\[\s*"(\d+)', response.content.decode('utf-8')):
            capture = match.group(1)
            counts.append(capture)
        self.assertContains(response, 'metric_value_1">' + counts[0])
        self.assertContains(response, 'metric_value_2">' + counts[1])

    def test_table_can_specify_report_period_days_in_url(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='data_date', report_period_days='3', debug=False)
        self.assertContains(response, 'metric_value_3')

    def test_table_can_specify_from_date_and_to_date_in_url(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='data_date', from_date='1-Nov-2018', to_date='04-Nov-2018', debug=False)
        self.assertContains(response, 'metric_value_4')


    #
    # Get KPI data in graph view
    #

    def test_can_get_kpi_graph_page_with_js_library(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='graph', debug=False)
        self.assertContains(response, 'Chart.bundle.js')

    def test_can_get_kpi_graph_page_with_a_dummy_graph(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='graph', debug=False)
        self._assertRegex(response, r'\d{4,}, \d{4,}')

    def test_get_kpi_graph_shows_kpi_value_for_each_day(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        date_1 = date.today() - timedelta(2)
        date_2 = date.today() - timedelta(1)
        date_1_string = str(int(date_1.strftime('%d'))) + '/' + str(int(date_1.strftime('%m')))  # 1/11
        date_2_string = str(int(date_2.strftime('%d'))) + '/' + str(int(date_2.strftime('%m')))  # 2/11
        response = self.get_graph(kpi='each_day', debug=False)
        self.assertContains(response, '"' + date_1_string + '", "' + date_2_string + '"')
        counts = []
        for match in re.finditer(r'counts":\[\s*"(\d+)', response.content.decode('utf-8')):
            capture = match.group(1)
            counts.append(capture)
        self.assertContains(response, counts[0] + ', ' + counts[1])

    def test_kpi_name_in_graph_label(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='visits_label', debug=False)
        self._assertRegex(response, r'label: .visits_label')

    def test_graph_can_specify_report_period_days_in_url(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='data_date', report_period_days='4', debug=False)
        self._assertRegex(response, r'\d+, \d+, \d+, \d+')

    def test_graph_can_specify_from_date_and_to_date_in_url(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='data_date', from_date='1-Nov-2018', to_date='04-Nov-2018', debug=False)
        self._assertRegex(response, r'\d+, \d+, \d+, \d+')


    #
    # Table / Graph common code
    #

    def test_to_date_cannot_be_greater_than_yesterday(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        from_date = date.today() - timedelta(2)
        to_date = date.today()
        # %d-%b 04-Nov http://strftime.org/
        response = self.get_graph(kpi='data_date', from_date=from_date.strftime('%d-%b'), to_date=to_date.strftime('%d-%b'), debug=False)
        self.assertContains(response, 'To date cannot be greater than yesterday')

    def test_from_date_cannot_be_greater_than_to_date(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        from_date = date.today() - timedelta(2)
        to_date = date.today() - timedelta(4)
        # %d-%b 04-Nov http://strftime.org/
        response = self.get_graph(kpi='data_date', from_date=from_date.strftime('%d-%b'), to_date=to_date.strftime('%d-%b'), debug=False)
        self.assertContains(response, 'From date cannot be greater than to date')

    def test_can_specify_report_suite_id_in_query_string(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='data_date', from_date='1-Nov-2018', to_date='04-Nov-2018', report_suite_id='my-cool-id', debug=False)
        self.assertContains(response, 'reportSuiteID":"my-cool-id')

    def test_debug_view_indicates_dashboard_not_defined(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_table(kpi='not_defined_dashboard', from_date='1-Nov-2018', to_date='04-Nov-2018', report_suite_id='my-cool-id', debug=False)
        self.assertContains(response, 'No dashboard with name not_defined_dashboard found, assuming it is a metric_id')

    def test_debug_view_indicates_dashboard_defined_and_used(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.submit_edit(kpi='defined_dashboard_id', metric_id='my_metric_id', metric_desc='Special Desc', default_report_period_days='4', default_report_suite_id='special-suite-id', debug=False)
        response = self.get_graph(kpi='defined_dashboard_id', debug=False)
        self.assertContains(response, 'Dashboard defined_dashboard_id found, with metric_id my_metric_id')
        self._assertRegex(response, r'\d+, \d+, \d+, \d+')
        self.assertContains(response, '"reportSuiteID":"special-suite-id"')
        self._assertRegex(response, 'label: .Special Desc')

    #
    # endpoint create/edit
    #

    def test_can_get_endpoint_page(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'Create / Edit Adobe Analytics Endpoint')
        self.assertContains(response, 'Endpoint test') # title
        self.assertContains(response, 'Endpoint Type')
        self.assertContains(response, '>test<')

    def test_endpoint_form_has_username_field(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'username')
        self.assertContains(response, 'class="narrow-input"')
        self.assertContains(response, 'API Username')

    def test_endpoint_form_has_secret_field(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'secret')
        self.assertContains(response, 'API Secret')
        self.assertContains(response, 'maxlength="50"')

    def test_endpoint_form_has_queue_url(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'queue_url')
        self.assertContains(response, 'Queue URL')
        self.assertContains(response, 'maxlength="200"')

    def test_endpoint_form_has_get_url(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'get_url')
        self.assertContains(response, 'Get URL')

    def test_endpoint_form_has_default_report_suite_id(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'default_report_suite_id')
        self.assertContains(response, 'Default Report Suite Id')

    def test_endpoint_form_has_default_report_period_days(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'default_report_period_days')
        self.assertContains(response, 'Default Report Period Days')
        self.assertContains(response, 'type="number" min="1" max="31"')

    def test_endpoint_form_has_blank_date_created(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'date_created')
        self.assertContains(response, 'Date Created')
        self.assertContains(response, 'id="id_date_created"><') # is blank

    def test_endpoint_form_has_blank_date_modified(self):
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'date_modified')
        self.assertContains(response, 'Date Modified')
        self.assertContains(response, 'id="id_date_modified"><') # is blank

    def test_endpoint_edit_dashboard_form_for_new_endpoint(self):
        response = self.submit_endpoint(type='fake', debug=False)
        self.assertContains(response, 'Endpoint config written to database ok')

    def test_endpoint_api_username_written_to_database(self):
        response = self.submit_endpoint(type='test', username='my_api_username', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'my_api_username')

    def test_endpoint_api_report_period_days_written_to_database(self):
        response = self.submit_endpoint(type='test', default_report_period_days='27', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, '"27"')

    def test_endpoint_default_report_suite_id_written_to_database(self):
        response = self.submit_endpoint(type='test', default_report_suite_id='my-special-id', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'my-special-id')

    def test_endpoint_secret_displays_empty_when_no_data(self):
        response = self.submit_endpoint(type='test', secret='', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'name="secret" value=""')
    
    def test_endpoint_secret_displays_eight_asterix_when_has_data(self):
        response = self.submit_endpoint(type='test', secret='my_api_secret', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'name="secret" value="********"')

    def test_endpoint_secret_does_not_update_when_eight_asterix_submitted(self):
        response = self.submit_endpoint(type='test', secret='my_api_secret', debug=False)
        self.assertContains(response, 'API Secret updated')
        response = self.submit_endpoint(type='test', secret='********', debug=False)
        self.assertContains(response, 'API Secret not updated')

    def test_endpoint_queue_url_written_to_database(self):
        response = self.submit_endpoint(type='test', queue_url='https://api', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'name="queue_url" value="https://api"')

    def test_endpoint_get_url_written_to_database(self):
        response = self.submit_endpoint(type='test', get_url='https://api_get', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self.assertContains(response, 'name="get_url" value="https://api_get"')

    def test_endpoint_date_created_visible_on_subsequent_form_get(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self._assertRegex(response, r'date_created">\w+\. \d+, \d{4,4}')

    def test_endpoint_date_modified_visible_on_subsequent_form_get(self):
        response = self.submit_endpoint(type='test', debug=False)
        response = self.get_endpoint(type='test', debug=False)
        self._assertRegex(response, r'date_modified">\w+\. \d+, \d{4,4}')


    #
    # Metric Cache
    #

    def test_production_metric_data_is_cached(self):
        response = self.submit_endpoint(type='prod', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='cache', from_date='1-Nov-2018', to_date='04-Nov-2018', endpoint='prod', debug=False)
        self._assertNotRegex(response, r'Metric data found in cache')
        counts = []
        for match in re.finditer(r'counts":\[\s*"(\d+)', response.content.decode('utf-8')):
            capture = match.group(1)
            counts.append(capture)
        response = self.get_graph(kpi='cache', from_date='1-Nov-2018', to_date='04-Nov-2018', endpoint='prod', debug=False)
        self._assertRegex(response, r'Metric data found in cache')
        self.assertContains(response, counts[0] + ', ' + counts[1] + ', ' + counts[2] + ', ' + counts[3])

    def test_test_metric_data_is_not_cached(self):
        response = self.submit_endpoint(type='test', default_report_period_days='2', debug=False)
        response = self.get_graph(kpi='not_cache', from_date='1-Nov-2018', to_date='04-Nov-2018', endpoint='prod', debug=False)
        self._assertNotRegex(response, r'Metric data found in cache')
        response = self.get_graph(kpi='not_cache', from_date='1-Nov-2018', to_date='04-Nov-2018', endpoint='test', debug=False)
        self._assertNotRegex(response, r'Metric data found in cache')


#    m = re.search(r'Result at: ([^\s]*)', result_stdout)
#    if (m):
#        return m.group(1)
#    else:
#        return '/DEV/Summary.xml'


# Tests
# - Create/Edit dashboard
#   * GET kpi/summary/edit/site_visits - does not exist
#       * username
#       * secret
#       * queue_url
#       * queue_body
#       * get_url
#       * get_body
#       * report_period_days
#       * date_created (will be blank) (display only)
#       * date_modified (will be blank) (display only)
#   - GET kpi/summary/edit/site_visits - does exist
#       - username
#       - secret
#       - queue_url
#       - queue_body
#       - get_url
#       - get_body
#       - report_period_days
#       - date_created (display only)
#       - date_modified (display only)
#   - POST kpi/summary/edit/site_visits - does not exist
#       - can post and get message
#       - data written to database
#   - POST kpi/summary/edit/site_visits - does exist
#   - stylesheet used
#   - kpi_name displayed in page heading
#   - username, secret, get_url, get_body is compulsory
#   - secret value is blank/masked, but new value can be added, if not changed, it isn't updated to blank or erroneous value in DB
#   - report period days is max 31 days

# MVP
# - Create/Edit dashboard
#   - GET kpi/summary/edit/site_visits will display the current fields for dashboard named site_visits, or blank if empty
#   - POST kpi/summary/edit/site_visits will update the fields to the database
# - Display dashboard as table
#   - GET kpi/summary/table/site_visits will display the kpi raw data for the report period
#   - will get and store missing data before display
#       - will request data for each day of the report period
#       - will retry 5 times before giving up
#       - will detect authentication error
#       - will detect time zone problem
#       - will detect invalid request
#   - returns error if dashboard does not exist
# - Fake Adobe Endpoint
#   - Endpoint returns 'You must post to this endpoint' on GET
#   - Checks for WSSE header
#   - Returns KPI data
# - Display dashboard as graph
#   - GET kpi/summary/graph/site_visits will graph the kpi for the report period
#   - will get missing data before display
