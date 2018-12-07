from django.db import models

# Create your models here.
class Dash(models.Model):
    kpi_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    secret = models.CharField(max_length=50)
    queue_url = models.CharField(max_length=200)
    queue_body = models.CharField(max_length=2000)
    get_url = models.CharField(max_length=200)
    get_body = models.CharField(max_length=2000)
    report_period_days = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class Endpoint(models.Model):
    endpoint_type = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    secret = models.CharField(max_length=50)
    queue_url = models.CharField(max_length=200)
    get_url = models.CharField(max_length=200)
    default_report_suite_id = models.CharField(max_length=50)
    default_report_period_days = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class KPI(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    date_modified = models.DateTimeField(auto_now=True)

class Queue(models.Model):
    report_id = models.CharField(max_length=20)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    metric_id = models.CharField(max_length=50)
    report_suite_id = models.CharField(max_length=50)
    date_granularity = models.CharField(max_length=10)
    date_created = models.DateTimeField(auto_now_add=True)
    get_requests = models.IntegerField(default=0)

