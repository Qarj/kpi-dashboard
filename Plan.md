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
    - [ ] Table shows Report.Get body in debug mode
    - [x] Table view has message if kpi is unknown
    - [ ] Request data for date range
        - [x] Calculate dateFrom and dateTo
        - [x] Substitute dateFrom, dateTo into Queue Body
        - [x] Generate WSSE header
        - [x] Post to Queue URL
            - [ ] Remember Report id (does not need to be put in DB)
        - [ ] Post to Get with response from Queue
            - [ ] Parse Adobe response into array
        - [ ] Return page with JavaScript graphing library pointing to array
- [ ] Create fake Adobe endpoint
    - method=Report.Queue
        - [ ] Must have content type header `Content-Type: application/json`
        - [x] Should return JSON object when posting to Queue
        - [x] Should return Report ID `{"reportID":3582786221}`
    - method=Report.Get
        - [x] Post reportID `{"reportID":3582786221}`
        - [x] Should return JSON Object
        - [ ] Should return a count for each day
        - [ ] Different random number for each day
        - [ ] Totals value is correct
        - [ ] Visits returned per day should be in range 100k to 200k
    - any method
        - [ ] Must have content type headaer
        - [ ] Presence of Username validated, if not present, actual error message returned
        - [ ] Presence of PasswordDigest validated, if not present, actual error message returned
        - [ ] Presence of Nonce validated, if not present, actual error message returned
        - [ ] Presence of Created validated, if not present, actual error message returned
        - [ ] Must have X-WSSE header `X-WSSE: UsernameToken Username="user:company", PasswordDigest="123==", Nonce="0b6f", Created="2018-11-19T03:01:29Z"`
        - [ ] Created should not be more than 5 mins in the future, if it is, actual error message returned
        - [ ] Created should not be more than 5 mins in the past, if it is, actual error message returned
        - [ ] Must have `Content-Type: application/json` header, else actual error message returned
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

