import json
import datetime
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import *
from itertools import chain
from celery_tasks.tasks import send_mail_task


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


# 判断预订时间是否冲突
def detect_time_conflict(date, classroom, start_time, end_time):
    tmp1 = ClassroomBooking.objects.filter(date=date, classroom=classroom,
                                           start_time__lte=start_time, end_time__gt=start_time).exclude(state=2)
    tmp2 = ClassroomBooking.objects.filter(date=date, classroom=classroom,
                                           start_time__lt=end_time, end_time__gte=end_time).exclude(state=2)
    if len(tmp1) != 0 or len(tmp2) != 0:
        return False  # can't book
    else:
        return True  # can book


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
        result['user_id'] = user.id
    else:
        result['success'] = False
        result['msg'] = "用户名或密码错误"
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
    classroom_name = request.POST.get("name")
    manager_name = request.POST.get("manager__username")
    classroom_state = request.POST.get("state")
    try:
        if classroom_state == "":
            classroom_list = Classroom.objects.\
                filter(name__contains=classroom_name, manager__username__contains=manager_name).\
                values('id', 'name', 'size', 'img', 'manager__username', 'state')
        else:
            classroom_list = Classroom.objects.\
                filter(name__contains=classroom_name, state=classroom_state, manager__username__contains=manager_name).\
                values('id', 'name', 'size', 'img', 'manager__username', 'state')
        result['num'] = len(classroom_list)
        result['classroom_list'] = list(classroom_list)
        result['success'] = True
    except ValueError:
        result['success'] = False
        result['msg'] = "参数存在无效数据，请重试"
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
# @login_required
def get_user_booking_list(request):
    result = {}
    user_id = request.POST.get("userid")
    if user_id is None or user_id == "":
        user_id = request.user.id
    try:
        booking_list = ClassroomBooking.objects.filter(user_id=user_id).values(
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
# @login_required
def create_booking(request):
    result = {}
    try:
        classroom_name = request.POST.get('classroom_name')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        user_id = request.POST.get('userid')

        classroom = Classroom.objects.get(name=classroom_name)
        if user_id is None or user_id == "":
            current_user = request.user
        else:
            current_user = User.objects.get(id=user_id)

        # 判断是否可以预订
        if detect_time_conflict(date, classroom, start_time, end_time):
            booking = ClassroomBooking(date=datetime.datetime.strptime(date, '%Y-%m-%d'),
                                       start_time=datetime.datetime.strptime(start_time, '%H:%M:%S'),
                                       end_time=datetime.datetime.strptime(end_time, '%H:%M:%S'),
                                       state=0, classroom=classroom, user=current_user)
            booking.save()
            result['success'] = True
        else:
            result['success'] = False
            result['msg'] = "时间冲突，无法预订"
    except ValueError:
        result['success'] = False
        result['msg'] = "参数存在无效数据，请重试"
    except Classroom.DoesNotExist:
        result['success'] = False
        result['msg'] = "教室名有误，请重试"
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 修改预订
@csrf_exempt
# @login_required
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

        if detect_time_conflict(date, classroom, start_time, end_time):
            booking.date = datetime.datetime.strptime(date, '%Y-%m-%d')
            booking.start_time = datetime.datetime.strptime(start_time, '%H:%M:%S')
            booking.end_time = datetime.datetime.strptime(end_time, '%H:%M:%S')
            booking.classroom = classroom
            booking.state = 0
            booking.save()
            result['success'] = True
        else:
            result['success'] = False
            result['msg'] = "时间冲突，无法修改预订"
    except ValueError:
        result['success'] = False
        result['msg'] = "参数存在无效数据，请重试"
    except ClassroomBooking.DoesNotExist:
        result['success'] = False
        result['msg'] = "订单号有误，请重试"
    except Classroom.DoesNotExist:
        result['success'] = False
        result['msg'] = "教室名有误，请重试"
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 删除预订
@csrf_exempt
# @login_required
def del_booking_by_id(request):
    result = {}
    try:
        booking_ids = request.POST.get('id')
        booking_id_list = booking_ids.split(',')
        for booking_id in booking_id_list:
            ClassroomBooking.objects.filter(id=booking_id).delete()
        result['success'] = True
    except ValueError:
        result['success'] = False
        result['msg'] = "参数有误，请检查后重试"
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 修改管理员信息
@csrf_exempt
#@login_required
def modify_admin_info_by_id(request):
    result = {}
    try:
        current_user = request.user
        new_name = request.POST.get('name')
        new_tel = request.POST.get('tel')
        userid = request.POST.get('userid')

        if userid is None:
            admin = UserInfo.objects.get(user=current_user)
        else:
            admin = UserInfo.objects.get(user_id=userid)
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

    booked_user = request.POST.get('booked_user')
    if booked_user is None:
        booked_user = ''
    start_date = request.POST.get('start_date')
    if start_date is None or start_date == '':
        start_date = '1970-1-1'
    end_date = request.POST.get('end_date')
    if end_date is None or end_date == '':
        end_date = '2199-1-1'
    booking_state = request.POST.get('state')
    if booking_state is None or booking_state == '':
        booking_state = list(range(10))
    try:
        booking_list = ClassroomBooking.objects.values(
            'id', 'classroom__name', 'date', 'start_time', 'end_time', 'state', 'user__username'
        ).filter(user__username__contains=booked_user, date__gte=start_date, date__lt=end_date, state__in=booking_state)
        content = list(booking_list)
        result['booking_list'] = content
        result['num'] = len(booking_list)
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 设置教室预定状态
@csrf_exempt
def set_booking_status(request):
    result = {}
    try:
        booking_ids = request.POST.get('id')
        booking_id_list = booking_ids.split(',')
        booking_status = request.POST.get('state')
        booking_status_list = booking_status.split(',')
        mail_content = {}
        for i in range(min(len(booking_id_list), len(booking_status_list))):
            booking = ClassroomBooking.objects.get(id=booking_id_list[i])
            booking.state = int(booking_status_list[i])
            booking.save()

            content = "您的预定：" + booking.date.strftime('%Y-%m-%d') + " " + booking.start_time.strftime('%H:%M:%S') \
                      + " - " + booking.end_time.strftime('%H:%M:%S') + " " + booking.classroom.name
            if int(booking_status_list[i]) == 1:
                content += "    审核通过\n"
            elif int(booking_status_list[i]) == 2:
                content += "    审核拒绝\n"

            if booking.user.email in mail_content:
                mail_content[booking.user.email] += content
            else:
                mail_content[booking.user.email] = content

        # 发送邮件
        for key, value in mail_content.items():
            if '@' in key:
                # send_mail(
                #     '教室预定审核状态变动',
                #     value,
                #     'lf97310@163.com',
                #     [key, 'lf97310@163.com'],
                #     fail_silently=False,
                # )
                send_mail_task.delay(value, key)
            else:
                print(key + " 邮箱地址错误")

        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 增加教室
@csrf_exempt
def add_classroom(request):
    result = {}
    try:
        manager_name = request.POST.get('manager__username')
        classroom_name = request.POST.get('name')
        classroom_size = request.POST.get('size')
        classroom_img = request.POST.get('img')
        classroom_state = request.POST.get('state')

        manager = User.objects.get(username=manager_name)
        classroom = Classroom(name=classroom_name, size=classroom_size, img=classroom_img, state=classroom_state,
                              manager=manager)
        classroom.save()
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")


# 删除教室
@csrf_exempt
def del_classroom_by_id(request):
    result = {}
    try:
        classroom_ids = request.POST.get('id')
        classroom_id_list = classroom_ids.split(',')
        for classroom_id in classroom_id_list:
            Classroom.objects.filter(id=classroom_id).delete()
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
        classroom_id = request.POST.get('id')
        manager_name = request.POST.get('manager__username')
        classroom_name = request.POST.get('name')
        classroom_size = request.POST.get('size')
        classroom_img = request.POST.get('img')
        classroom_state = request.POST.get('state')

        manager = User.objects.get(username=manager_name)
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


# 注册
@csrf_exempt
def user_register(request):
    result = {}
    username = request.POST.get("username")
    password = request.POST.get("password")
    checkpwd = request.POST.get("checkpwd")
    email = request.POST.get("email")
    name = request.POST.get("name")
    tel = request.POST.get("tel")
    if password != checkpwd:
        result['success'] = False
        result['msg'] = '两次输入密码不一样'
    else:
        if User.objects.filter(username=username).first():
            result['success'] = False
            result['msg'] = "该用户名已存在"
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            userinfo = UserInfo(user=user, name=name, tel=tel, user_type=2)
            userinfo.save()
            result['success'] = True
    return HttpResponse(json.dumps(result), content_type="application/json")


# 修改密码
@csrf_exempt
# @login_required
def modify_password(request):
    result = {}
    try:
        # user = request.user
        user_id = request.POST.get("user_id")
        user = User.objects.get(id=user_id)
        password = request.POST.get("password")
        newpwd = request.POST.get("newpwd")
        ret = user.check_password(password)
        if ret:
            user.set_password(newpwd)
            user.save()
            result['success'] = True
        else:
            result['success'] = False
            result['msg'] = "原密码输入错误"
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result), content_type="application/json")


# 查看个人信息
@csrf_exempt
# @login_required
def get_personal_info(request):
    result = {}
    try:
        user_id = request.POST.get("user_id")
        current_user = request.user
        personal_info_list = UserInfo.objects.get(user_id=user_id)
        user = User.objects.get(id=personal_info_list.user_id)
        result['id'] = personal_info_list.user_id
        result['name'] = personal_info_list.name
        result['tel'] = personal_info_list.tel
        result['email'] = user.email
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result), content_type="application/json")


# 修改个人信息
@csrf_exempt
# @login_required
def modify_personal_info(request):
    result = {}
    try:
        user_id = request.POST.get("user_id")
        current_user = request.user
        name = request.POST.get("name")
        tel = request.POST.get("tel")
        email = request.POST.get("email")
        userinfo = UserInfo.objects.get(user_id=user_id)
        userinfo.name = name
        userinfo.tel = tel
        userinfo.save()
        user = User.objects.get(id=userinfo.user_id)
        user.email = email
        user.save()
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result), content_type="application/json")


# 查看本人历史预定情况
@csrf_exempt
# @login_required
def get_history_booking_list(request):
    result = {}
    try:
        user_id = request.POST.get("user_id")
        current_user = request.user
        booking_list = ClassroomBooking.objects.filter(user_id=user_id, state=1).values(
            'id', 'classroom__name', 'date', 'start_time', 'end_time', 'state'
        )
        result['booking_list'] = list(booking_list)
        result['success'] = True
    except Exception as e:
        result['success'] = False
        result['msg'] = repr(e)
    return HttpResponse(json.dumps(result, cls=DateEncoder), content_type="application/json")