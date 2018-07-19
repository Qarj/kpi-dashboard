# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

def index(request):
    page_title = "KPI Dashboard"
    page_heading = "KPI Dashboard"
    error = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'error': error,
    }

    return render(request, 'summary/index.html', context)
