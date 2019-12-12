import json

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return HttpResponse("Hello World !!!")


@csrf_exempt
def user_login(request):
    result = {}
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        result['success'] = True
    else:
        result['success'] = False
    return HttpResponse(json.dumps(result), content_type="application/json")


@csrf_exempt
def user_logout(request):
    result = {}
    try:
        logout(request)
        result['success'] = True
    except:
        result['success'] = False
    return HttpResponse(json.dumps(result), content_type="application/json")


