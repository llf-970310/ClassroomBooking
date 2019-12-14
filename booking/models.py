from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField('姓名', max_length=100)
    tel = models.CharField('联系电话', max_length=100)
    user_type = models.IntegerField('用户类型')


class Classroom(models.Model):
    name = models.CharField('教室名', max_length=100)
    size = models.IntegerField('教室大小')
    img = models.CharField('教室图片', max_length=100)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.BooleanField('是否开放预定')


class ClassroomBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField('日期')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    state = models.IntegerField('预定状态')
