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
    desired_date = date.today() + timedelta(offset)
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

    # def runit(self, path, debug=False, batch='', target=''):
        # kwargs={'path': path}
        # if (batch):
            # kwargs['batch'] = batch
        # if (target):
            # kwargs['target'] = target
        # url = my_reverse('server:run', query_kwargs=kwargs)
        # return self._get_url(url, debug)

    # def get_submit(self, debug=False, batch='', target='', name=''):
        # return self._get_url( self._build_submit_url(batch, target, name), debug )

    # def canary(self, debug=False):
        # url = my_reverse('server:canary')
        # return self._get_url( url, debug )

    def adobe_fake_api(self, body, debug=False, method=''):
        my_date = '8888-88-88'
        return self._post_url_and_body( self._build_adobe_fake_api_url(method), body, debug )

    def _build_adobe_fake_api_url(self, method):
        kwargs={}
        if (method):
            kwargs['method'] = method
        return my_reverse('summary:adobe_fake_api', query_kwargs=kwargs)

    # def _get_url(self, url, debug=False):
        # response = self.client.get(url)
        # if (debug):
            # print('\nDebug URL:', url)
            # print(response.content.decode('utf-8'), '\n')
        # return response

    def _post_url_and_body(self, url, body, debug=False):
#        response = self.client.post(url, json.dumps(body), format='json')
        response = self.client.generic('POST', url, json.dumps(body))
        if (debug):
            print('\nDebug URL :', url)
            print('\nDebug Body:', body)
            print('\nDebug Response Content Start\n', response.content.decode('utf-8'), '\n')
            print('\nDebug Response Content End\n')
        return response

    def _assertRegex(self, response, regex):
        self.assertRegex(response.content.decode('utf-8'), regex)

    def _assertNotRegex(self, response, regex):
        self.assertNotRegex(response.content.decode('utf-8'), regex)

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
        response = self.adobe_fake_api(build_visits_body(kpi_date(-1)), method='Report.Run', debug=True)
        self._assertRegex(response, r'"visits":"\d{5,}"')
        
        
# Tests
# MVP
# - Fake Adobe Endpoint
#   - Endpoint returns 'You must post to this endpoint' on GET
#   - Checks for WSSE header
#   - Returns KPI data
# - Create/Edit dashboard
#   - GET kpi/summary/edit/site_visits will display the current fields for dashboard named site_visits, or blank if empty
#   - POST kpi/summary/edit/site_visits will update the fields to the database
# - Display dashboard as table
#   - GET kpi/summary/table/site_visits will display the kpi raw data for the report period
#   - will get missing data before display
# - Display dashboard as graph
#   - GET kpi/summary/table/site_visits will graph the kpi for the report period
#   - will get missing data before display
