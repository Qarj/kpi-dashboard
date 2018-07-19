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
-[ ] Create new Django project kpi
-[ ] Fix WSGI.py
-[ ] Create dash schema (username, secret, request url, request body, report_last_days, kpi_name)
-[ ] Create kpi schema (date, value)
-[ ] Generate WSSE header
-[ ] Create mock Adobe endpoint
-[ ] Parse Adobe response
-[ ] Put response in DB
-[ ] Determine missing data and request in loop

## Tasks - Later
-[ ] graph previous period - week
-[ ] graph previous period - year
