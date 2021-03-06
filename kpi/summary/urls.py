from django.urls import path

from . import views

app_name = 'summary'

urlpatterns = [
    # ex: /kpi/summary/
    path('', views.index, name='index'),

    # ex: /kpi/summary/adobe/
    path('adobe/', views.adobe, name='adobe'),

    # ex: /kpi/summary/adobe_fake_api/?method=Report.Run
    path('adobe_fake_api/', views.adobe_fake_api, name='adobe_fake_api'),

    # ex: /kpi/summary/edit/kpi_visits/
    path('edit/<kpi>/', views.edit, name='edit'),

    # ex: /kpi/summary/endpoint/test/ ex: /kpi/summary/endpoint/prod/
    path('endpoint/<type>/', views.endpoint, name='endpoint'),

    # ex: /kpi/summary/table/kpi_visits/
    path('table/<kpi>/', views.table, name='table'),

    # ex: /kpi/summary/table/kpi_visits/7/
    path('table/<kpi>/<report_period_days>/', views.table, name='table'),

    # ex: /kpi/summary/table/kpi_visits/1-Nov/4-Nov/
    path('table/<kpi>/<from_date>/<to_date>/', views.table, name='table'),

    # ex: /kpi/summary/graph/kpi_visits/
    path('graph/<kpi>/', views.graph, name='graph'),

    # ex: /kpi/summary/graph/kpi_visits/7/
    path('graph/<kpi>/<report_period_days>/', views.graph, name='graph'),

    # ex: /kpi/summary/graph/kpi_visits/1-Nov/4-Nov/
    path('graph/<kpi>/<from_date>/<to_date>/', views.graph, name='graph'),

    # ex: /kpi/summary/canary/
#    path('canary/', views.canary, name='canary'),
]