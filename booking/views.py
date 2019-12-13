import json

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.csrf import csrf_exempt
from .models import *


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


# 查看教室基本信息
@csrf_exempt
def get_classroom_info(request):
    result = {}
    classroom_id = request.POST.get("id")
    try:
        if classroom_id != "":
            classroom_item = Classroom.objects.filter(id=classroom_id).values()
            result['num'] = 1
            result['classroom_list'] = list(classroom_item)
        else:
            classroom_list = Classroom.objects.all().values()
            result['num'] = len(classroom_list)
            result['classroom_list'] = list(classroom_list)
        result['success'] = True
    except:
        result['success'] = False
    return HttpResponse(json.dumps(result), content_type="application/json")



