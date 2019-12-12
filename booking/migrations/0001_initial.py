# Generated by Django 3.0 on 2019-12-12 08:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='教室名')),
                ('size', models.IntegerField(verbose_name='教室大小')),
                ('img', models.CharField(max_length=100, verbose_name='教室图片')),
                ('state', models.BooleanField(verbose_name='是否开放预定')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='姓名')),
                ('tel', models.CharField(max_length=100, verbose_name='联系电话')),
                ('user_type', models.IntegerField(verbose_name='用户类型')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='日期')),
                ('start_time', models.TimeField(verbose_name='开始时间')),
                ('end_time', models.TimeField(verbose_name='结束时间')),
                ('state', models.IntegerField(verbose_name='预定状态')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.Classroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]