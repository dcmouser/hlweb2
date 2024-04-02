from django.shortcuts import render
from django.http import HttpResponse

def homePageView(request):
    return HttpResponse("Hello, world - from games.")