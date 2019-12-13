import json
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.csrf import csrf_exempt
from .models import *


# 解决返回 json 中日期格式序列化的问题
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


# Create your views here.
def index(request):
    return HttpResponse("Hello World !!!")


# 登录
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


# 登出
@csrf_exempt
def user_logout(request):
    result = {}
    try:
        logout(request)
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result), content_type="application/json")


# 查看教室基本信息
@csrf_exempt
def get_classroom_info(request):
    result = {}
    classroom_id = request.POST.get("id")
    try:
        if classroom_id != "":
            classroom_item = Classroom.objects.filter(id=classroom_id).values(
                'id', 'name', 'size', 'img', 'manager__username', 'state'
            )
            result['num'] = 1
            result['classroom_list'] = list(classroom_item)
        else:
            classroom_list = Classroom.objects.all().values()
            result['num'] = len(classroom_list)
            result['classroom_list'] = list(classroom_list)
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result), content_type="application/json")


# 查看当前用户预订列表
@csrf_exempt
@login_required
def get_user_booking_list(request):
    result = {}
    try:
        booking_list = ClassroomBooking.objects.filter(user_id=request.user.id).values(
            'id', 'classroom__name', 'date', 'start_time', 'end_time', 'state'
        )
        result['booking_list'] = list(booking_list)
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 修改预订
@csrf_exempt
@login_required
def modify_booking_by_id(request):
    result = {}
    try:
        booking_id = request.POST.get('id')
        classroom_name = request.POST.get('classroom_name')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        booking = ClassroomBooking.objects.get(id=booking_id)
        classroom = Classroom.objects.get(name=classroom_name)
        booking.date = datetime.datetime.strptime(date, '%Y-%m-%d')
        booking.start_time = datetime.datetime.strptime(start_time, '%H:%M:%S')
        booking.end_time = datetime.datetime.strptime(end_time, '%H:%M:%S')
        booking.classroom = classroom
        booking.save()

        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 删除预订
@csrf_exempt
@login_required
def del_booking_by_id(request):
    result = {}
    try:
        booking_ids = request.POST.get('id')
        booking_id_list = booking_ids.split(',')
        for booking_id in booking_id_list:
            ClassroomBooking.objects.filter(id=booking_id).delete()
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


