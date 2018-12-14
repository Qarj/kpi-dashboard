# kpi-dashboard
Goal is to slurp metrics from an Adobe Analytics KPI and show it on dashboard.

## Initial features wish list
- Configure a dashboard - define the api request to collect data at a day level (not hourly), and number of days to go back and collect data
- When dashboard started, it will go back and attempt to collect missing data for the report period, will be stored locally
- On a subsequent day, will get yesterday's results, then display the graph for report period using JavaScript
- Cycle through dashboards mode
- Select dashboard to display
- Credentials and API payload saved in the dashboard database (not in git!)
- resilient to transient network / server issues

## Later features wish list
- Update and display KPI on a hourly basis

## Tasks - MVP
- [x] Create new Django project kpi `django-admin startproject kpi & cd kpi & python manage.py runserver`
- [x] Create new app `python manage.py startapp summary`
- [x] Add app to `kpi/settings.py`: `'summary.apps.SummaryConfig',`
- [x] In settings.py fix Timezone `TIME_ZONE = 'UTC'`
- [x] In settings.py set static url `STATIC_URL = '/kpi-static/'`
- [x] Fix WSGI.py `os.environ['DJANGO_SETTINGS_MODULE'] = 'kpi.settings'`
- [x] in `kpi/urls.py` add include `from django.urls import include, path` and url pattern `path('summary/', include('summary.urls')),`
- [x] create `summary/urls.py`
- [x] .gitignore
- [x] Create dash schema - username, secret, request url, request body, report_last_days, kpi_name
- [x] Create kpi schema - date, value
- [x] Need to make migrations before running any tests, e.g. `delete_dashboard_then_create_empty.py`
- [x] A simple test passes
- [x] Create favicon
- [x] Get running under Apache
- Edit KPI
    - [x] API `username` update
    - [x] API `secret` update
        - [x] secret is blank when no data
        - [x] secret is 8x asterix on form when data exists
        - [x] secret is only updated to the database when value other than 8x asterix submitted
    - [x] `queue_url` update
    - [x] `queue_body` update
    - [x] `get_url` update
    - [x] `get_body` update
    - [x] `report_period_days` update
        - [x] Max Value of 31
        - [x] Min Value of 1
        - [x] Must be an integer
    - [x] `date_created` contains date on first submit
    - [x] `date_modified` contains date on first submit
    - [x] Example Queue request is updated to current plan
- [ ] Table for KPI /kpi/summary/table/kpi_visits/ (tests use fake endpoint)
    - [x] Table view has heading
    - [x] Table view has title
    - [x] Table view shows number of days requested
    - [x] Table view shows fromDate in format required by Adobe
    - [x] Table view shows toDate in format required by Adobe
    - [x] Show from and to dates in table
    - [x] Table view shows calculated Report.Queue body in ?debug=true mode
    - [x] Table view shows calculated X-WSSE header in ?debug=true mode
        - [x] Username component
        - [x] Password digest component
        - [x] Nonce component
        - [x] Created component
    - [x] Table view shows content type header in ?debug=true mode
    - [x] Table shows Queue URL in debug mode
    - [x] Table shows Get URL in debug mode
    - [x] Table view has message if kpi is unknown
    - [x] Table - request data for date range
        - [x] Calculate dateFrom and dateTo
        - [x] Substitute dateFrom, dateTo into Queue Body
        - [x] Generate WSSE header
        - [x] Post to Queue URL
            - [x] Remember Report id reponse (does not need to be put in DB)
        - [x] Post to Get with response from Queue
            - [x] Parse Adobe response into array
        - [x] Show table response, one table row per day
        - [x] Handle report not yet ready error
            - [x] Wait 2 seconds, then try again
                - [x] for fake urls, wait 0 seconds
                - [x] double wait time after each failure
            - [x] Timeout of 3 attempts
    - [x] Refactor Table so bulk of code can be shared with Graph
    - [x] Graph
        - [x] load chart.bundle.js
        - [x] get working with some hard coded dummy data
        - [x] real dates are inserted into labels array - check with http://127.0.0.1:8000/summary/graph/site_visits_43/?debug=true
        - [x] real values are inserted into data array
        - [x] kpi_name inserted into label
    - [x] Endpoint
        - [x] Create endpoint view as a copy of edit
        - [x] endpoint_type instead of kpi_name
        - [x] Strip out Report.Queue - this is now hard coded
        - [x] Strip out Report.Get - now hard coded
        - [x] Rename report_period_days to default_report_period_days
        - [x] Add default_report_suite_id
        - [x] Endpoint has its own model separate to the one used by edit (Dash)
    - [ ] Refactor Edit
        - [x] Remove Report.Queue
        - [x] Remove Report.Get
        - [x] Remove API Username
        - [x] Remove API Secret
        - [x] Add default_report_suite_id
        - [x] Add default_report_period_days
        - [x] Add metric_id
        - [ ] table/graph will first check see if kpi_name exists
            - [ ] If so, use details from it
            - [ ] If not, use default details from endpoint, assuming that kpi_name == metric_id
    - [ ] Refactor Table/Graph to use new paradigm
    	- [x] Hard code to Report.Queue body
    	- [x] Add query string endpoint=test to all test calls to Table/Graph
    	- [x] Tests create Endpoint record as well as Edit record
    	- [x] metric_id is read from URL (kpi)
    	- [x] Get info from Endpoint table, intstead of Dash
    		- [x] Username
    		- [x] Password
    		- [x] Queue URL
    		- [x] Get URL
    		- [x] Report Period Days
    		- [x] Report Suite Id
    	- [x] Remove creation of Edit record from bulk of tests
        - [x] Endpoint defaults to 'prod'
        - [x] Endpoint can be changed to 'test' with ?endpoint=test query string parm
        - [x] Can put number of days in: summary/table/visits/60 is last 60 days
        - [x] Can put date range in: summary/table/visits/20-Oct/10-Nov
        - [x] Can change report_suite_id: summary/table/visits/20-Oct/10-Nov?report_suite_id=my-id
            - [x] table
            - [x] graph
        - [x] Throw error if to_date is > yesterday
        - [x] Throw error if from_date > to_date
        - [ ] Adobe error messages displayed (needs test)
- [ ] Create fake Adobe endpoint
    - method=Report.Queue
        - [ ] Must have content type header `Content-Type: application/json`
        - [x] Should return JSON object when posting to Queue
        - [x] Should return Report ID `{"reportID":3582786221}`
        - [ ] Find out what Authentication Error message looks like (use wrong secret)
        - [ ] Return correct error code on Authentication Error (400?)
    - method=Report.Get
        - [x] Post reportID `{"reportID":3582786221}`
        - [x] Should return JSON Object
        - [x] Should return a JSON Object like the real one - for one day with visits count 123456
        - [x] Should return a count for each day - for multiple days
        - [x] Different random number for each day
        - [x] Totals value is correct
        - [x] Visits returned per day should be in range 100k to 250k (no test)
        - [x] Period from date is correct
        - [x] Period to date is correct
        - [x] Date name in data is correct
        - [x] Date year, month and day in data is correct
        - [x] Metrics id is correct
        - [x] Metrics name matches id with first letter capital
        - [x] Can delete a specifed Report Id (for test purposes)
        - [x] Will return a report not ready error on first request (for known report ids)
            - [x] Find out what report not ready error looks like
        - [x] Will return report on second request
        - [x] Should return 400 when report not ready
    - any method
        - [ ] Must have content type header
        - [ ] Presence of Username validated, if not present, actual error message returned
        - [ ] Presence of PasswordDigest validated, if not present, actual error message returned
        - [ ] Presence of Nonce validated, if not present, actual error message returned
        - [ ] Presence of Created validated, if not present, actual error message returned
        - [ ] Must have X-WSSE header `X-WSSE: UsernameToken Username="user:company", PasswordDigest="123==", Nonce="0b6f", Created="2018-11-19T03:01:29Z"`
        - [ ] Created should not be more than 5 mins in the future, if it is, actual error message returned
        - [ ] Created should not be more than 5 mins in the past, if it is, actual error message returned
        - [ ] Must have `Content-Type: application/json` header, else actual error message returned
- [ ] Cache
    - [x] New Model metric_id, report_suite_id, metric_date, value, date_modified
    - [x] Attempt to find metric in Cache first
        - [x] Debug mode indicates cache hit
    - [x] If full request needed, update Cache afterwards
    - [ ] Delete cache metric id
    - [ ] Delete catch entirely
    - [x] Cache can be poisoned by requesting metrics for current day, throw error if to_date is after yesterday
    - [ ] Does one DB call make more sense than many?
    - [ ] Cache should not be updated if cache_hit
- [x] Deployment
    - [x] mod-wsgi fix for Django
	- [x] Linux config added to test-results-dashboard
    - [x] Fix: `ALLOWED_HOSTS = ['*']`
	- [x] Deployment instructions for Linux
	- [x] Deployment instructions for Windows
- [ ] Canary
    - [ ] Fake endpoint responds to POST Report.Queue
    - [ ] Fake endpoint responds to POST Report.Get
- [x] Spike - get metric report for a date range
```
{
    "reportDescription":{
        "reportSuiteID":"my-brand-id",
        "dateFrom":"2018-11-12",
        "dateTo":"2018-11-19",
        "dateGranularity":"day",
        "metrics":[
            {
                "id":"visits"
            }
        ]
    }
}
```


## Tasks - Later
-[ ] graph previous period - week
-[ ] graph previous period - year

## Util

http://localhost/kpi/summary/
http://127.0.0.1:8000/summary

Restart Apache - must be ADMINISTRATOR
```
echo must be ADMIN, will pretend to work if not, but will fail
\Apache24\bin\httpd -k restart
```

References:
- https://github.com/dancingcactus/python-omniture
- X-WSSE https://gist.github.com/bebehei/5e3357e5a1bf46ec381379ef8f525c7f
- X-WSSE https://forums.adobe.com/ideas/10397
- X-WSSE https://forums.adobe.com/thread/2405028  (errors)

