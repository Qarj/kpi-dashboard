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

    # ex: /kpi/summary/table/kpi_visits/
    path('table/<kpi>/', views.table, name='table'),

    # ex: /kpi/summary/canary/
#    path('canary/', views.canary, name='canary'),
]