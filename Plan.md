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
