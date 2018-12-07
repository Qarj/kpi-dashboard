# kpi-dashboard
Display KPIs on a dashboard using Adobe Analytics API 1.4

KPI documentation: https://github.com/AdobeDocs/analytics-1.4-apis

## Dashboard Home
http://localhost/kpi/summary/

## Create / Edit endpoint

http://localhost/kpi/summary/endpoint/prod/
http://localhost/kpi/summary/endpoint/test/

## Table view

http://localhost/kpi/summary/table/visits/
http://localhost/kpi/summary/table/visits/31
http://localhost/kpi/summary/table/visits/1-Nov/20-Nov
http://localhost/kpi/summary/table/visits/1-Nov-2017/20-Nov-2018

### Override the endpoint (default is prod)
http://localhost/kpi/summary/table/visits/?endpoint=test

### Debug mode
http://localhost/kpi/summary/table/visits/?debug=true

## Graph view

Same urls as table view, except s/table/graph/

## Create / Edit kpi

http://localhost/kpi/summary/edit/< KPI NAME >/
http://localhost/kpi/summary/edit/site_visits/

# Linux Deployment

Deploy the following project to satisfy Apache configuration dependencies:
- https://github.com/Qarj/test-results-dashboard

Create a folder for webimblaze-server and clone the project:
```
cd /var/www
sudo mkdir kpi
sudo chmod 777 kpi
cd kpi
sudo git clone https://github.com/Qarj/kpi-dashboard
```

Set permissions so the Apache user can access the file system:
```
cd /var/www/kpi
sudo find . -type d -exec chmod a+rwx {} \;
sudo find . -type f -exec chmod a+rw {} \;
sudo find . -type f -iname "*.py" -exec chmod +x {} \;
```

Restart Apache:
```
sudo systemctl restart apache2
```

Verify with url: http://localhost/kpi/summary/endpoint/test/

### Debugging

```
sudo cat /etc/apache2/envvars
sudo cat /var/log/apache2/error.log
```



# Fake Adobe API

### Home page: http://localhost/kpi/summary/adobe

### Queue request

What|Desc
----|----
URL | http://localhost/kpi/summary/adobe_fake_api/?method=Report.Queue
Method| POST
Header| `Content-Type: application/json`
Header| `X-WSSE: UsernameToken Username="user:company", PasswordDigest="123==", Nonce="0b6f", Created="2018-11-19T03:01:29Z"`
Body| JSON - see below
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

Example response:
```
{"reportID":3582786221}
```

Note that the Content-Type of `application/json` doesn't seem to be required, posting with `application/x-www-form-urlencoded`
seems to work also.


X-WSSE present, but with typo - Usergame
```
{
   "error":"Bad Request",
   "error_description":"Authentication key not found",
   "error_uri":null
}
```

X-WSSE token not present
```
{
   "error":"Bad Request",
   "error_description":"Invalid authentication credentials.",
   "error_uri":null
}
```

PasswortDigest, or Ponce, 
```
{  
   "error":"Bad Request",
   "error_description":"Unable to validate authentication.",
   "error_uri":null
}
```

Creates instead of Created 
```
{  
   "error":"Bad Request",
   "error_description":"Invalid created timestamp (''). Values should be in ISO-8601 format",
   "error_uri":null
}
```

Created time out of sync
```
{
   "error":"Bad Request",
   "error_description":"The specified created timestamp ('2018-11-22T23:22:12Z') has expired or is in the future",
   "error_uri":null
}
```


### Get request

What|Desc
----|----
URL | http://localhost/kpi/summary/adobe_fake_api/?method=Report.Get
Method| POST
Header| `Content-Type: application/json`
Header| `X-WSSE: UsernameToken Username="user:company", PasswordDigest="123==", Nonce="0b6f", Created="2018-11-19T03:01:29Z"`
Body| `{"reportID":3582786221}`

Example response:
```
{
   "report":{
      "type":"overtime",
      "elements":[
         {
            "id":"datetime",
            "name":"Date"
         }
      ],
      "reportSuite":{
         "id":"my-brand-id",
         "name":"Example Website"
      },
      "period":"Mon. 12 Nov. 2018 - Mon. 19 Nov. 2018",
      "metrics":[
         {
            "id":"visits",
            "name":"Visits",
            "type":"number",
            "decimals":0,
            "latency":1577,
            "current":false
         }
      ],
      "data":[
         {
            "name":"Mon. 12 Nov. 2018",
            "year":2018,
            "month":11,
            "day":12,
            "counts":[
               "14319"
            ]
         },
         {
            "name":"Tue. 13 Nov. 2018",
            "year":2018,
            "month":11,
            "day":13,
            "counts":[
               "14040"
            ]
         },
         {
            "name":"Wed. 14 Nov. 2018",
            "year":2018,
            "month":11,
            "day":14,
            "counts":[
               "14291"
            ]
         },
         {
            "name":"Thu. 15 Nov. 2018",
            "year":2018,
            "month":11,
            "day":15,
            "counts":[
               "13156"
            ]
         },
         {
            "name":"Fri. 16 Nov. 2018",
            "year":2018,
            "month":11,
            "day":16,
            "counts":[
               "10898"
            ]
         },
         {
            "name":"Sat. 17 Nov. 2018",
            "year":2018,
            "month":11,
            "day":17,
            "counts":[
               "7290"
            ]
         },
         {
            "name":"Sun. 18 Nov. 2018",
            "year":2018,
            "month":11,
            "day":18,
            "counts":[
               "7320"
            ]
         },
         {
            "name":"Mon. 19 Nov. 2018",
            "year":2018,
            "month":11,
            "day":19,
            "counts":[
               "13501"
            ]
         }
      ],
      "totals":[
         "94815"
      ],
      "version":"1.4.18.10"
   },
   "waitSeconds":0,
   "runSeconds":0
}
```

Report not ready:
```
{
   "error":"report_not_ready",
   "error_description":"Report not ready",
   "error_uri":null
}
```

Report id unknown to Adobe:
```
{
   "error":"report_id_invalid",
   "error_description":"Invalid report ID",
   "error_uri":null
}
```

