from django.http import HttpResponse
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'index.html')
def routeResponse(request):
    response_data = {}
    response_data['1'] = 'request'
    response_data['message'] = 'Some error message'
    return HttpResponse(response_data)