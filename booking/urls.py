"""classroom_booking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('get_classroom_info', views.get_classroom_info, name='get_classroom_info'),
    path('get_user_booking_list', views.get_user_booking_list, name='get_user_booking_list'),
    path('del_booking_by_id', views.del_booking_by_id, name='del_booking_by_id'),
    path('modify_booking_by_id', views.modify_booking_by_id, name='modify_booking_by_id'),
    path('get_classroom_booking', views.get_classroom_booking, name='get_classroom_booking'),
    path('create_booking', views.create_booking, name='create_booking'),
    path('modify_admin_info_by_id', views.modify_admin_info_by_id, name='modify_admin_info_by_id'),
    path('get_booking_list', views.get_booking_list, name='get_booking_list'),
    path('set_booking_status', views.set_booking_status, name='set_booking_status'),
    path('modify_classroom_by_id', views.modify_classroom_by_id, name='modify_classroom_by_id'),
    path('register', views.user_register, name='register'),
    path('modify_password', views.modify_password, name='modify_password'),
    path('modify_personal_info', views.modify_personal_info, name='modify_personal_info'),
    path('get_history_booking_list', views.get_history_booking_list, name='get_history_booking_list')
]
