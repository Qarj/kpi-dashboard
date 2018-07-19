# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode

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

    # def submit(self, steps, debug=False, batch='', target='', name=''):
        # body = {'steps': steps}
        # return self._post_url_and_body( self._build_submit_url(batch, target, name), body, debug )

    # def _build_submit_url(self, batch, target, name):
        # kwargs={}
        # if (batch):
            # kwargs['batch'] = batch
        # if (target):
            # kwargs['target'] = target
        # if (name):
            # kwargs['name'] = name
        # return my_reverse('server:submit', query_kwargs=kwargs)

    # def _get_url(self, url, debug=False):
        # response = self.client.get(url)
        # if (debug):
            # print('\nDebug URL:', url)
            # print(response.content.decode('utf-8'), '\n')
        # return response

    # def _post_url_and_body(self, url, body, debug=False):
        # response = self.client.post(url, body)
        # if (debug):
            # print('\nDebug URL :', url)
            # print('\nDebug Body:', body)
            # print('\nDebug Response Content Start\n', response.content.decode('utf-8'), '\n')
            # print('\nDebug Response Content End\n')
        # return response

    # def number_of_instances(self, response, target):
        # return response.content.decode('utf-8').count(target)

    # def _assertRegex(self, response, regex):
        # self.assertRegex(response.content.decode('utf-8'), regex)

    # def _assertNotRegex(self, response, regex):
        # self.assertNotRegex(response.content.decode('utf-8'), regex)

    def test_fake_adobe_returns_message_on_GET(self):
        response = self.client.get(reverse('summary:adobe'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fake Adobe KPI endpoint')
        
        
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
