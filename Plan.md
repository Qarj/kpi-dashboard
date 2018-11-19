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
    - [ ] API Username update
    - [ ] API Secret update
    - [ ] Queue URL update
    - [ ] Queue Body update
    - [ ] Get URL update
    - [ ] Get Body update
    - [ ] Report Period Days update
        - [ ] Max Value of 31
        - [ ] Min Value of 1
        - [ ] Must be an integer
    - [ ] Date Created contains date after first submit
    - [ ] Date Modified contains date after first submit
    - [ ] Date Created and Date Modifed are equal after first submit
    - [ ] Date Modified is > Date Modified on subsequent submit
- [ ] Table for KPI /kpi/summary/table/kpi_visits/ (tests use fake endpoint)
    - [ ] Determine missing data and request in loop
        - [ ] All data is missing
        - [ ] Partial data is missing
        - [ ] Generate WSSE header
        - [ ] Post to Queue
            - [ ] Remember Report id (does not need to be put in DB)
        - [ ] Post to Get
            - [ ] Parse Adobe response
            - [ ] Put response in DB Date, Value
        - [ ] Return Table once all data found
            - [ ] Column 1 - Date
            - [ ] Column 2 - KPI value
- [ ] Create fake Adobe endpoint
    - method=Report.Queue
        - [ ] Must have content type header `Content-Type: application/json`
        - [ ] Must have X-WSSE header `X-WSSE: UsernameToken Username="user:company", PasswordDigest="123==", Nonce="0b6f", Created="2018-11-19T03:01:29Z"`
        - [ ] Should return JSON object when posting to Queue
        - [ ] Should return Report ID `{"reportID":3582786221}`
    - method=Report.Get
        - [ ] Post reportID `{"reportID":3582786221}`
        - [ ] Must have content type headaer
        - [ ] Should return JSON Object
        - [x] Visits returned should be at least 100k
- [ ] Canary
    - [ ] Fake endpoint responds to POST Report.Queue
    - [ ] Fake endpoint responds to POST Report.Get

## Tasks - Later
-[ ] graph previous period - week
-[ ] graph previous period - year

## Util

http://localhost/kpi/summary/

Restart Apache
```
\Apache24\bin\httpd -k restart
```
