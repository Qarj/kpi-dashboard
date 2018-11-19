# kpi-dashboard
Display KPIs on a dashboard

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
        "date":"2018-11-18",
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
         "id":"my-website-brand",
         "name":"Example Website"
      },
      "period":"Mon. 12 Nov. 2018",
      "metrics":[
         {
            "id":"visits",
            "name":"Visits",
            "type":"number",
            "decimals":0,
            "latency":3807,
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
               "14302"
            ]
         }
      ],
      "totals":[
         "14302"
      ],
      "version":"1.4.18.10"
   },
   "waitSeconds":0,
   "runSeconds":0
}{
   "report":{
      "type":"overtime",
      "elements":[
         {
            "id":"datetime",
            "name":"Date"
         }
      ],
      "reportSuite":{
         "id":"my-website-brand",
         "name":"Example Website"
      },
      "period":"Mon. 12 Nov. 2018",
      "metrics":[
         {
            "id":"visits",
            "name":"Visits",
            "type":"number",
            "decimals":0,
            "latency":3807,
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
               "14302"
            ]
         }
      ],
      "totals":[
         "14302"
      ],
      "version":"1.4.18.10"
   },
   "waitSeconds":0,
   "runSeconds":0
}
```

