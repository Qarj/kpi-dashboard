# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from datetime import date, timedelta
import json

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
    desired_date = date.today() - timedelta(offset)
    return desired_date.strftime("%Y-%m-%d")

#target_date = '9999-99-99'
    
def build_visits_body(target_date):
    return \
{
    "reportDescription":{
        "reportSuiteID":"my_brand",
        "date":target_date,
        "dateGranularity":"day",
        "metrics":[
            {
                "id":"visits"
            }
        ]
    }
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

    def get_table(self, debug=False, kpi='unknown', page_debug='true'):
        return self._get_url( self._build_table_url(kpi, page_debug), debug )

    def _build_table_url(self, kpi, page_debug):
        kwargs={}
        kwargs['kpi'] = kpi
        query_kwargs={}
        query_kwargs['debug'] =  page_debug
        return my_reverse('summary:table', kwargs=kwargs, query_kwargs=query_kwargs)

    def get_edit(self, debug=False, kpi='unknown'):
        return self._get_url( self._build_edit_url(kpi), debug )

    def _build_edit_url(self, kpi):
        kwargs={}
        kwargs['kpi'] = kpi
        return my_reverse('summary:edit', kwargs=kwargs)

    def submit_edit(self, kpi, username='default_username', report_period_days=7, secret='default_secret',
                    queue_url='http://default_queue',
                    queue_body="""
{
    "reportDescription":{
        "reportSuiteID":"my-brand-id",
        "dateFrom":"{DATE_FROM}",
        "dateTo":"{DATE_TO}",
        "dateGranularity":"day",
        "metrics":[
            {
                "id":"visits"
            }
        ]
    }
}
""",
                    get_url='http://default_get',
                    get_body='default get body',
                    debug=False):
        body = {
                    'username': username,
                    'secret': secret,
                    'queue_url': queue_url,
                    'queue_body': queue_body,
                    'get_url': get_url,
                    'get_body': get_body,
                    'report_period_days': report_period_days,
        }
        return self._post_url_and_body( self._build_edit_url(kpi), body, debug=debug )

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

    def test_adobe_fake_api_returns_JSON_on_POST(self):
        response = self.adobe_fake_api(build_visits_body(kpi_date(-1)), method='Report.Run', debug=False)
        self._assertRegex(response, r'"visits":"\d+"')

    def test_adobe_fake_api_returns_message_on_GET(self):
        response = self.client.get(reverse('summary:adobe_fake_api'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Must be a post request')

    def test_adobe_fake_api_returns_random_visits_greater_than_100k(self):
        response = self.adobe_fake_api(build_visits_body(kpi_date(-1)), method='Report.Run', debug=False)
        self._assertRegex(response, r'"visits":"\d{5,}"')


    #
    # Create / Edit KPI form
    #

    def test_can_get_kpi_edit_page(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'Create / Edit KPI Dashboard')
        self.assertContains(response, 'Edit site_visits')
        self.assertContains(response, 'KPI Name')
        self.assertContains(response, '>site_visits<')

    def test_edit_page_form_has_username_field(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'username')
        self.assertContains(response, 'class="narrow-input"')
        self.assertContains(response, 'API Username')

    def test_edit_page_form_has_secret_field(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'secret')
        self.assertContains(response, 'API Secret')
        self.assertContains(response, 'maxlength="50"')

    def test_edit_page_form_has_queue_url(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'queue_url')
        self.assertContains(response, 'Queue URL')
        self.assertContains(response, 'maxlength="200"')

    def test_edit_page_form_has_queue_body(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'queue_body')
        self.assertContains(response, 'Queue Body')
        self.assertContains(response, 'maxlength="2000"')

    def test_edit_page_form_has_get_url(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'get_url')
        self.assertContains(response, 'Get URL')

    def test_edit_page_form_has_get_body(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'get_body')
        self.assertContains(response, 'Get Body')

    def test_edit_page_form_has_report_period_days(self):
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'report_period_days')
        self.assertContains(response, 'Report Period Days')
        self.assertContains(response, 'type="number" min="1" max="31"')

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

    def test_api_username_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', username='my_api_username', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'my_api_username')

    def test_api_report_period_days_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', report_period_days='27', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '"27"')

    def test_secret_displays_empty_when_no_data(self):
        response = self.submit_edit(kpi='site_visits', secret='', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'name="secret" value=""')
    
    def test_secret_displays_eight_asterix_when_has_data(self):
        response = self.submit_edit(kpi='site_visits', secret='my_api_secret', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'name="secret" value="********"')

    def test_secret_does_not_update_when_eight_asterix_submitted(self):
        response = self.submit_edit(kpi='site_visits', secret='my_api_secret', debug=False)
        self.assertContains(response, 'API Secret updated')
        response = self.submit_edit(kpi='site_visits', secret='********', debug=False)
        self.assertContains(response, 'API Secret not updated')

    def test_queue_url_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', queue_url='https://api', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'name="queue_url" value="https://api"')

    def test_queue_body_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', queue_body='{ queued: true }', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '{ queued: true }')

    def test_get_url_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', get_url='https://api_get', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, 'name="get_url" value="https://api_get"')

    def test_get_body_written_to_database(self):
        response = self.submit_edit(kpi='site_visits', get_body='{ report_id: 42 }', debug=False)
        response = self.get_edit(kpi='site_visits', debug=False)
        self.assertContains(response, '{ report_id: 42 }')

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
        response = self.submit_edit(kpi='table', debug=False)
        response = self.get_table(kpi='table', debug=False)
        self.assertContains(response, 'table view for KPI table')

    def test_get_kpi_table_title(self):
        response = self.submit_edit(kpi='title', debug=False)
        response = self.get_table(kpi='title', debug=False)
        self.assertContains(response, 'title table')

    def test_get_kpi_table_num_days(self):
        response = self.submit_edit(kpi='title', report_period_days='7', debug=False)
        response = self.get_table(kpi='title', debug=False)
        self.assertContains(response, '7 days table view')

    def test_get_kpi_table_datefrom(self):
        response = self.submit_edit(kpi='range', report_period_days='2', debug=False)
        response = self.get_table(kpi='range', debug=False)
        self.assertContains(response, 'dateFrom">' + kpi_date(2))

    def test_get_kpi_table_dateto(self):
        response = self.submit_edit(kpi='range', report_period_days='2', debug=False)
        response = self.get_table(kpi='range', debug=False)
        self.assertContains(response, 'dateTo">' + kpi_date(1))

    def test_get_kpi_table_dateto(self):
        response = self.submit_edit(kpi='range', report_period_days='2', debug=False)
        response = self.get_table(kpi='range', debug=False)
        self.assertContains(response, 'dateTo">' + kpi_date(1))

    def test_get_kpi_table_debug_info_only_shown_in_debug_mode(self):
        response = self.submit_edit(kpi='debug', report_period_days='2', debug=False)
        response = self.get_table(kpi='debug', page_debug='false', debug=False)
        self._assertNotRegex(response, r'dateFrom')

    def test_get_kpi_table_shows_substituted_report_queue_body(self):
        response = self.submit_edit(kpi='queue_body', report_period_days='2', debug=False)
        response = self.get_table(kpi='queue_body', debug=False)
        self.assertContains(response, 'dateGranularity')
        self.assertContains(response, 'dateFrom&quot;:&quot;' + kpi_date(2))

    def test_get_kpi_table_shows_x_wsse_header_in_debug_mode(self):
        response = self.submit_edit(kpi='x-wsse_username', username="my:user", debug=False)
        response = self.get_table(kpi='x-wsse_username', debug=False)
        self.assertContains(response, 'Username=&quot;my:user&quot;')
        self.assertContains(response, 'PasswordDigest=')
        self.assertContains(response, 'Nonce=')
        self.assertContains(response, 'Created=')

    def test_get_kpi_table_shows_content_type_header_in_debug_mode(self):
        response = self.submit_edit(kpi='content_type', username="my:user", debug=False)
        response = self.get_table(kpi='content_type', debug=False)
        self.assertContains(response, 'application/json')

    def test_get_kpi_table_shows_message_when_kpi_not_defined(self):
        response = self.get_table(kpi='unknown_kpi_definition', debug=False)
        self.assertContains(response, 'unknown_kpi_definition has not been defined')


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
