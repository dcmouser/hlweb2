from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

def homePageView(request):
    #return HttpResponse("Hello, world - from games.")
    name = "myworld"
    return render(request, "base.html", {"name": name})
