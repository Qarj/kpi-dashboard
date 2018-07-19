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
- [ ] Get running under Apache
- [ ] Create mock Adobe endpoint
- [ ] Generate WSSE header
- [ ] Parse Adobe response
- [ ] Put response in DB
- [ ] Determine missing data and request in loop

## Tasks - Later
-[ ] graph previous period - week
-[ ] graph previous period - year
