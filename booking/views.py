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
        result['user_type'] = UserInfo.objects.get(user_id=user.id).user_type
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


# 查看教室预订情况
@csrf_exempt
def get_classroom_booking(request):
    result = {}
    classroom_id = request.POST.get("id")
    try:
        if classroom_id != "":
            booking_item = ClassroomBooking.objects.filter(classroom_id=classroom_id).values(
                'id', 'date', 'start_time', 'end_time', 'state', 'classroom__name', 'user__username'
            )
            result['booking_list'] = list(booking_item)
        else:
            booking_list = ClassroomBooking.objects.all().values(
                'id', 'date', 'start_time', 'end_time', 'state', 'classroom__name', 'user__username'
            )
            result['booking_list'] = list(booking_list)
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


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


# 新增预订
@csrf_exempt
@login_required
def create_booking(request):
    result = {}
    try:
        classroom_name = request.POST.get('classroom_name')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        classroom = Classroom.objects.get(name=classroom_name)
        current_user = request.user

        # 判断是否可以预订
        tmp1 = ClassroomBooking.objects.filter(date=date, classroom=classroom,
                                               start_time__lte=start_time, end_time__gt=start_time)
        tmp2 = ClassroomBooking.objects.filter(date=date, classroom=classroom,
                                               start_time__lt=end_time, end_time__gte=end_time)
        if len(tmp1) != 0 or len(tmp2) != 0:
            result['success'] = False
            result['msg'] = "时间冲突，无法预订"
        else:
            booking = ClassroomBooking(date=datetime.datetime.strptime(date, '%Y-%m-%d'),
                                       start_time=datetime.datetime.strptime(start_time, '%H:%M:%S'),
                                       end_time=datetime.datetime.strptime(end_time, '%H:%M:%S'),
                                       state=0, classroom=classroom, user=current_user)
            booking.save()
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
        booking.state = 0
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


# 修改管理员信息
@csrf_exempt
@login_required
def modify_admin_info_by_id(request):
    result = {}
    try:
        admin_id = request.POST.get('id')
        new_name = request.POST.get('name')
        new_tel = request.POST.get('tel')

        admin = UserInfo.objects.get(id=admin_id)
        admin.name = new_name
        admin.tel = new_tel
        admin.save()
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 获取所有预定信息
@csrf_exempt
def get_booking_list(request):
    result = {}
    try:
        booking_list = ClassroomBooking.objects.values(
            'id', 'classroom_name', 'date', 'start_time', 'end_time', 'state'
        )
        result['booking_list'] = list(booking_list)
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 设置预定状态
@csrf_exempt
def set_booking_status(request):
    # todo: 这里status的表达方式还未确定
    result = {}
    try:
        booking_ids = request.POST.get('id')
        booking_id_list = booking_ids.split(',')
        booking_status = request.POST.get('status')
        booking_status_list = booking_status.split(',')
        for i in range(min(len(booking_id_list), len(booking_status_list))):
            ClassroomBooking.objects.get(id=booking_id_list[i]).state = booking_status_list[i]
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 更改教室信息
@csrf_exempt
def modify_classroom_by_id(request):
    result = {}
    try:
        classroom_id = request.POST.get('classroom_id')
        manager_id = request.POST.get('manager_id')
        classroom_name = request.POST.get('name')
        classroom_size = request.POST.get('size')
        classroom_img = request.POST.get('img')
        classroom_state = request.POST.get('state')

        manager = UserInfo.objects.get(id=manager_id)
        classroom = Classroom.objects.get(id=classroom_id)
        classroom.name = classroom_name
        classroom.size = classroom_size
        classroom.img = classroom_img
        classroom.state = classroom_state
        classroom.manager = manager
        classroom.save()
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")
