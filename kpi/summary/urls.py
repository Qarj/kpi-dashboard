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

    # ex: /kpi/summary/table/
#    path('table/', views.table, name='table'),

    # ex: /kpi/summary/canary/
#    path('canary/', views.canary, name='canary'),
]