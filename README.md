# kpi-dashboard
Display KPIs on a dashboard using Adobe Analytics API 1.4

KPI documentation: https://github.com/AdobeDocs/analytics-1.4-apis

## Dashboard Home
http://localhost/kpi/summary/

## Create / Edit kpi

http://localhost/kpi/summary/edit/< KPI NAME >/
http://localhost/kpi/summary/edit/site_visits/


## Fake Adobe API
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

