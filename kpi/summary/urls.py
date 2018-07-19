from django.urls import path

from . import views

app_name = 'summary'

urlpatterns = [
    # ex: /kpi/summary/
    path('', views.index, name='index'),

    # ex: /kpi/summary/table/
#    path('table/', views.table, name='table'),

    # ex: /kpi/summary/canary/
#    path('canary/', views.canary, name='canary'),
]