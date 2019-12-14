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
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('get_classroom_info', views.get_classroom_info, name='get_classroom_info'),
    path('get_user_booking_list', views.get_user_booking_list, name='get_user_booking_list'),
    path('del_booking_by_id', views.del_booking_by_id, name='del_booking_by_id'),
    path('modify_booking_by_id', views.modify_booking_by_id, name='modify_booking_by_id')
]
