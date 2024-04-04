from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render



def homePageView(request):
    return render(request, "core/home.html")


def aboutPageView(request):
    return render(request, "core/about.html")
